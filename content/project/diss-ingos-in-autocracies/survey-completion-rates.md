Title: Survey completion rates
Date: 2016-06-09
Modified: 2016-06-09 16:15:38
Slug: survey-completion-rates
Tags: survey
Highlight: True
Plotly: True
UseTOC: True
Math: True

# Load and process all data


```r
library(dplyr)
library(tidyr)
library(stringr)
library(yaml)
library(purrr)
library(pander)
library(ggplot2)
library(ggrepel)
library(scales)
library(lubridate)
library(plotly)

panderOptions('table.split.table', Inf)
panderOptions('table.split.cells', Inf)
panderOptions('keep.line.breaks', TRUE)
panderOptions('table.style', 'multiline')
panderOptions('table.alignment.default', 'left')
```

## Dead addresses, domains, and bounces


```r
# Load data from tracking database
db.email <- src_sqlite(path=file.path(PROJHOME, "Data", "Survey", "list", 
                                      "final_list.db"))
email.full <- tbl(db.email, "full_list") %>% collect() %>%
  separate(id_org, c("db", "id.in.db"))
removed <- tbl(db.email, "remove") %>% collect()
bounced.raw <- tbl(db.email, "bounces") %>% collect()
completed <- tbl(db.email, "survey_completed") %>% collect()
sending.groups <- tbl(db.email, "groups") %>% collect()

email.by.db <- email.full %>%
  group_by(db) %>%
  summarise(num.apparently.valid = n())

dead.searches <- paste(c("Hippo", "Invalid", "Dead", "weird opt"), collapse="|")
dead <- removed %>%
  filter(str_detect(remove_notes, regex(dead.searches, ignore_case=TRUE))) %>%
  select(fk_org, notes = remove_notes)

bounced <- bounced.raw %>%
  gather(notes, value, hard_bounce, email_dead, email_bounce) %>%
  filter(value != 0) %>%
  select(fk_org, notes)
  
dead.and.bounced <- bind_rows(dead, bounced) %>%
  group_by(fk_org) %>%
  slice(1) %>%  # Get rid of duplicate removal entries
  ungroup() %>%
  left_join(select(email.full, fk_org = index_org, db), by="fk_org")

dead.and.bounced.by.db <- dead.and.bounced %>%
  group_by(db) %>%
  summarise(num.dead.bounced = n())
```

## Summarize response rates from each database


```r
# Load YAML metadata for survey lists
raw.lists <- yaml.load_file(file.path(PROJHOME, "data", "data_raw",
                                      "NGO lists", "ngo_lists.yml"),
                            as.named.list=TRUE)

# Convert to nice dataframe with purrr::map_df()
list.details <- seq(1:length(raw.lists$lists)) %>%
  map_df(function(x) raw.lists$lists[[x]][c("title", 'name',
                                            "num_rows_raw", "description")]) %>%
  arrange(desc(num_rows_raw))

response.summary <- list.details %>%
  left_join(email.by.db, by=c("name" = "db")) %>%
  left_join(dead.and.bounced.by.db, by=c("name" = "db")) %>%
  mutate(num.invited = num.apparently.valid - num.dead.bounced) %>%
  select(-c(description, name))

response.summary.total <- response.summary %>%
  summarise_each(funs(sum), -title) %>%
  mutate(title = "**Total**")

response.summary.with.total <- bind_rows(response.summary,
                                         response.summary.total) %>%
  mutate(perc.valid = num.apparently.valid / num_rows_raw,
         perc.bounced.from.valid = num.dead.bounced / num.apparently.valid,
         perc.invited.from.raw = num.invited / num_rows_raw,
         perc.invited.from.valid = num.invited / num.apparently.valid)

response.summary.display <- response.summary.with.total %>%
  mutate_each(funs(comma), starts_with("num")) %>%
  mutate_each(funs(percent), starts_with("perc"))
```

Full technical details of how I ran the survey are available at my [research
notebook](https://notebook.andrewheiss.com/project/diss-ingos-in-autocracies/survey-technical-details/).

The complete database of NGOs to receive a survey invitation came from 
5 different sources. After collecting the details
of each organization listed at each source, I cleaned the raw lists by 
removing all organizations without valid e-mail addresses and by attempting 
to filter out obviously domestic NGOs. I filtered out domestic NGOs either 
by not collecting them in the first place (in the case of the Yearbook of
International Organizations), or using information from the database to
identify them. For example, the UN iCSCO database includes a field for an
organization's geographic scope: local, national, regional, and
international. I omitted local and national.

I filtered out invalid e-mail addresses using Email Hippo, which pings each
address to verify (1) that the domain exists, and (2) that the address
exists at the domain.




```r
pandoc.table(response.summary.display)
```


-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
title                                                   num_rows_raw   num.apparently.valid   num.dead.bounced   num.invited   perc.valid   perc.bounced.from.valid   perc.invited.from.raw   perc.invited.from.valid  
------------------------------------------------------- -------------- ---------------------- ------------------ ------------- ------------ ------------------------- ----------------------- -------------------------
UN Integrated Civil Society Organizations System (iCSO) 27,028         7,498                  1,101              6,397         27.7%        14.7%                     23.7%                   85.3%                    

Directory of Development Organizations                  14,834         14,540                 7,457              7,083         98.0%        51.3%                     47.7%                   48.7%                    

Yearbook of International Organizations (YBIO)          9,325          3,065                  322                2,743         32.9%        10.5%                     29.4%                   89.5%                    

Global Anti-Human Trafficking (TIP) NGOs                1,421          1,063                  93                 970           74.8%        8.7%                      68.3%                   91.3%                    

Arab Institute of Human Rights NGO directory            761            606                    209                397           79.6%        34.5%                     52.2%                   65.5%                    

**Total**                                               53,369         26,772                 9,182              17,590        50.2%        34.3%                     33.0%                   65.7%                    
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Figure out partials, incompletes, completes

Determine the best cutoff point for partially answered questions based on
the number of questions answered.



```r
# Load full survey data (minus the Q4\* loop for simplicity)
survey.orgs.all <- readRDS(file.path(PROJHOME, "Data", "data_processed", 
                                     "survey_orgs_all.rds"))

# Load cleaned, country-based survey data (*with* the Q4\* loop)
survey.clean.all <- readRDS(file.path(PROJHOME, "Data", "data_processed", 
                                      "survey_clean_all.rds"))
```

What was the minimum number of questions answered by an INGO that finished
the survey?



```r
complete.ingos <- survey.orgs.all %>%
  filter(Finished == 1, Q2.4 == "Yes") %>%
  # Count of Q* questions answered
  mutate(num.answered = rowSums(!is.na(select(., starts_with("Q")))))

min(complete.ingos$num.answered)
```

```
## [1] 17
```

Thus, my rough cut-off point for partials = 20.

But, joining survey.orgs.all to survey.countries.all filters out all
respondents who did not answer anything in the loop of country questions.
That's not a problem, though, since the minimum number of questions answered
by one of these partials is higher than 20:



```r
partials <- survey.clean.all %>%
  filter(Finished == 0) %>%
  mutate(num.answered = rowSums(!is.na(select(., starts_with("Q"))))) %>%
  filter(num.answered >= 20)

min(partials$num.answered)
```

```
## [1] 27
```

So, I count any respondent that answered at least one question in the loop
of country questions. Doing so means that (1) they made it far enough into
the survey, and (2) shared *something* about how they relate to the
governments they work in. It's also a more conservative cutoff than simply
choosing a 20-question minimum arbitrarily.

Thus, there are this many valid partial responses:



```r
length(unique(partials$ResponseID))
```

```
## [1] 75
```

# Survey meta-metrics

## Absorption rate

> The absorption rate [measures] the ability of the survey company to manage
and keep up-to-date their database of email addresses and communications
with panel members [@CallegaroDiSogra:2008, 1026].

$$
\frac{EI - BB - NET}{EI}
$$


```r
EI <- response.summary.total$num.apparently.valid
BB.NET <- response.summary.total$num.dead.bounced

absorption.rate <- (EI - BB.NET) / EI
```

- EI = e-mail invitations sent: 26,772
- BB = bounced: 9,182
- NET = network undeliverable: included in `BB`
- **Absorption rate:** 65.7%

## Break-off rate

> The break-off rate is a possible indicator of problems in the design of
the questionnaire (e.g., too long, boring…) or struggle with technical
problems during the survey administration (e.g., streaming media or
animations that may “break” a survey at some point) 
[@CallegaroDiSogra:2008, 1026].

$$
\frac{BO}{I + P + BO}
$$



```r
# Only consider the organizations that were not screened out
survey.orgs.ingos <- survey.orgs.all %>%
  filter(Q2.4 == "Yes")

BO <- survey.orgs.ingos %>%
  filter(!(ResponseID %in% unique(c(partials$ResponseID,
                                    survey.clean.all$ResponseID)))) %>%
  select(ResponseID) %>% unique() %>% nrow() %>% unlist()

I.survey <- survey.clean.all %>%
  filter(Finished == 1) %>% select(ResponseID) %>% 
  unique() %>% nrow() %>% unlist()

P.survey <- length(unique(partials$ResponseID))

break.off.rate <- BO / (I.survey + P.survey + BO)
```

- BO = number of surveys broken off (i.e. incomplete and 
  not partial): 252
- I = complete: 490
- P = partial: 75
- **Break-off rate:** 30.8% 

## Completion rate (participation rate)

> The most intuitive response metric is the survey's completion rate. It is
also the one metric most often mislabeled as a response rate. The completion
rate is the proportion of those who completed the Web survey among all the
eligible panel members who were invited to take the survey
[@CallegaroDiSogra:2008, 1021-22].

> Using such a rate as an indicator of possible nonresponse error makes
little sense; however, the participation rate may serve as a useful
indicator of panel efficiency [@AAPOR:2016, 49].

$$
\frac{I + P}{(I + P) + (R + NC + O)}
$$



```r
# Number who refused (i.e. explicitly did not give consent)
R.survey <- survey.orgs.all %>%
  select(Q6.1) %>%
  filter(!is.na(Q6.1)) %>%
  nrow() %>% unlist()
```

Non-contact is impossible to determine, since I don't know how many
organizations self-screened without taking the survey or e-mailing me. So,
this participation rate is not accurate, but no participation rate ever is.


```r
NC <- response.summary.total$num.invited - nrow(survey.orgs.all)

participation.rate <- (I.survey + P.survey) / 
  (I.survey + P.survey + BO + R.survey + NC)
```

- I = complete: 490
- P = partial: 75
- R = refusal and break-off: 252 (break-off) and 
  2 (refusal)
- NC = non-contact: 16,037
- O = other: None
- **Participation rate**: 3.35%

## Study-specific screening completion rates

> Study-specific screening completion rates and eligibility rates measure
the incidence of a particular phenomenon among panel members. When these
rates are significantly different from an external "gold standard," they may
indicate issues of question wording in the screener module or respondents
purposively self-selecting themselves for a particular study (e.g., to gain
rewards) even if they do not really qualify.… These rates may also reveal a
skew in the panel membership along a particular dimension that may raise
concerns regarding bias [@CallegaroDiSogra:2008, 1026].

$$
\frac{SCQ + SCNQ}{INV}
$$



```r
SCQ <- survey.orgs.all %>%
  filter(Q2.4 == "Yes") %>%
  select(ResponseID) %>%
  unique() %>% nrow() %>% unlist()

SCNQ <- survey.orgs.all %>%
  filter(Q2.4 == "No") %>%
  select(ResponseID) %>%
  unique() %>% nrow() %>% unlist()

INV <- response.summary.total$num.invited

screening.completion.rate <- (SCQ + SCNQ) / INV
```

- SCQ = screening completed and qualified: 817
- SCNQ = screening completed and not qualified (i.e. screened out): 421
- INV = survey invitations sent out: 17,590
- **Study-specific screening completion rate**: 7.04%

## Study-specific eligibility rate

> The problem with a screening rate is that nonresponse is confounded with
the screening. In fact, we do not know if a person qualifies unless they
provide that information by answering the screening questions. For this
reason, we talk about screening completion rate and not screening rate
[@CallegaroDiSogra:2008, 1023].

$$
\frac{SCQ}{SCQ + SCNQ}
$$



```r
study.eligibility.rate <- SCQ / (SCQ + SCNQ)
```

- SCQ = screening completed and qualified: 817
- SCNQ = screening completed and not qualified (i.e. screened out): 421
- **Study-specific eligibility rate**: 66%

# Other details

> In addition to these rates, we also believe that it is the best practice
to report the length of the field period with its start and close dates, the
number of reminders sent and their form (email, letter, IVR call, or
personal call), and the use of any incentive [@CallegaroDiSogra:2008, 1026].

## Timeline of e-mail invitations


```r
invited.groups.summary <- email.full %>%
  filter(!(index_org %in% dead.and.bounced$fk_org)) %>%
  mutate(id_group = as.integer(group)) %>%
  group_by(id_group) %>%
  summarise(num.in.group = n())

sending.groups.summary <- sending.groups %>%
  left_join(invited.groups.summary, by="id_group") %>%
  # Because I stupidly didn't include a final reminder column, I put the
  # timestamp of the final reminder in the notes column. This extracts the
  # timestamp with a regex.
  mutate(email_final_reminder = 
           str_extract(notes, "\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}")) %>%
  mutate_each(funs(ymd_hms), starts_with("email")) %>%
  gather(email_type, email_date, starts_with("email"))


make_range <- function(x) {
  if (length(x) == 1) {
    return(paste("Group", as.character(x)))
  } else {
    return(paste0("Groups ", min(x), "-", max(x)))
  }
}

sending.groups.plot <- sending.groups.summary %>%
  mutate(email_day = ceiling_date(email_date, unit="day")) %>%
  filter(!is.na(email_day)) %>%
  group_by(email_day, email_type) %>%
  summarise(emails_sent = sum(num.in.group),
            group_names = make_range(id_group)) %>%
  ungroup() %>%
  mutate(total = cumsum(emails_sent),
         email_type = factor(email_type, 
                             levels=c("email_invitation", "email_reminder", 
                                      "email_final_reminder"),
                             label=c("Invitation  ", "Reminder  ", "Final reminder"),
                             ordered=TRUE))

plot.timeline <- ggplot(sending.groups.plot, aes(x=email_day, y=total)) +
  geom_step(size=0.5, colour="grey50") + 
  scale_y_continuous(labels=comma) +
  scale_x_datetime(date_labels="%B %e", date_breaks="1 week") +
  guides(fill=FALSE, colour=guide_legend(title=NULL)) +
  labs(x=NULL, y="Approximate total number of emails") +
  theme_light()

plot.timeline.static <- plot.timeline + 
  geom_point(aes(color=email_type)) + 
  geom_label_repel(aes(label=group_names, fill=email_type),
                   size=2.5, colour="white") +
  theme(legend.position="bottom", 
        legend.key.size=unit(0.65, "lines"),
        legend.key=element_blank(),
        panel.grid.minor=element_blank())

plot.timeline.interactive <- plot.timeline +
  geom_point(aes(color=email_type, text=group_names))

ggplotly(plot.timeline.interactive)
```

<!--html_preserve--><div id="htmlwidget-8762" style="width:672px;height:480px;" class="plotly html-widget"></div>
<script type="application/json" data-for="htmlwidget-8762">{"x":{"data":[{"x":[1461196800,1461283200,1461369600,1461888000,1461974400,1462233600,1462320000,1462924800,1465257600,1465344000,1465344000],"y":[1293,3003,4223,6725,8093,16955,21178,33910,46642,50865,51500],"text":["email_day: 2016-04-20 20:00:00<br>total: 1293","email_day: 2016-04-21 20:00:00<br>total: 3003","email_day: 2016-04-22 20:00:00<br>total: 4223","email_day: 2016-04-28 20:00:00<br>total: 6725","email_day: 2016-04-29 20:00:00<br>total: 8093","email_day: 2016-05-02 20:00:00<br>total: 16955","email_day: 2016-05-03 20:00:00<br>total: 21178","email_day: 2016-05-10 20:00:00<br>total: 33910","email_day: 2016-06-06 20:00:00<br>total: 46642","email_day: 2016-06-07 20:00:00<br>total: 50865","email_day: 2016-06-07 20:00:00<br>total: 51500"],"key":null,"type":"scatter","mode":"lines","name":"","line":{"width":1.88976377952756,"color":"rgba(127,127,127,1)","dash":"solid","shape":"hv"},"showlegend":false,"xaxis":"x","yaxis":"y","hoverinfo":"text"},{"x":[1461196800,1461283200,1461369600,1461888000,1461974400,1462233600,1465344000],"y":[1293,3003,4223,6725,8093,16955,51500],"text":["email_day: 2016-04-20 20:00:00<br>total: 1293<br>email_type: Invitation  <br>Groups 1-3","email_day: 2016-04-21 20:00:00<br>total: 3003<br>email_type: Invitation  <br>Groups 4-6","email_day: 2016-04-22 20:00:00<br>total: 4223<br>email_type: Invitation  <br>Groups 7-8","email_day: 2016-04-28 20:00:00<br>total: 6725<br>email_type: Invitation  <br>Groups 10-13","email_day: 2016-04-29 20:00:00<br>total: 8093<br>email_type: Invitation  <br>Groups 14-15","email_day: 2016-05-02 20:00:00<br>total: 16955<br>email_type: Invitation  <br>Groups 16-28","email_day: 2016-06-07 20:00:00<br>total: 51500<br>email_type: Invitation  <br>Group 9"],"key":null,"type":"scatter","mode":"markers","marker":{"autocolorscale":false,"color":"rgba(248,118,109,1)","opacity":1,"size":5.66929133858268,"symbol":"circle","line":{"width":1.88976377952756,"color":"rgba(248,118,109,1)"}},"name":"Invitation  ","legendgroup":"Invitation  ","showlegend":true,"xaxis":"x","yaxis":"y","hoverinfo":"text"},{"x":[1462320000,1462924800],"y":[21178,33910],"text":["email_day: 2016-05-03 20:00:00<br>total: 21178<br>email_type: Reminder  <br>Groups 1-8","email_day: 2016-05-10 20:00:00<br>total: 33910<br>email_type: Reminder  <br>Groups 10-28"],"key":null,"type":"scatter","mode":"markers","marker":{"autocolorscale":false,"color":"rgba(0,186,56,1)","opacity":1,"size":5.66929133858268,"symbol":"circle","line":{"width":1.88976377952756,"color":"rgba(0,186,56,1)"}},"name":"Reminder  ","legendgroup":"Reminder  ","showlegend":true,"xaxis":"x","yaxis":"y","hoverinfo":"text"},{"x":[1465257600,1465344000],"y":[46642,50865],"text":["email_day: 2016-06-06 20:00:00<br>total: 46642<br>email_type: Final reminder<br>Groups 10-28","email_day: 2016-06-07 20:00:00<br>total: 50865<br>email_type: Final reminder<br>Groups 1-8"],"key":null,"type":"scatter","mode":"markers","marker":{"autocolorscale":false,"color":"rgba(97,156,255,1)","opacity":1,"size":5.66929133858268,"symbol":"circle","line":{"width":1.88976377952756,"color":"rgba(97,156,255,1)"}},"name":"Final reminder","legendgroup":"Final reminder","showlegend":true,"xaxis":"x","yaxis":"y","hoverinfo":"text"}],"layout":{"margin":{"b":27.8953922789539,"l":66.1519302615193,"t":27.1581569115816,"r":7.97011207970112},"plot_bgcolor":"rgba(255,255,255,1)","paper_bgcolor":"rgba(255,255,255,1)","font":{"color":"rgba(0,0,0,1)","family":"","size":15.9402241594022},"xaxis":{"type":"linear","autorange":false,"tickmode":"array","range":[1460989440,1465551360],"ticktext":["April 25","May  2","May  9","May 16","May 23","May 30","June  6"],"tickvals":[1461542400,1462147200,1462752000,1463356800,1463961600,1464566400,1465171200],"ticks":"outside","tickcolor":"rgba(179,179,179,1)","ticklen":3.98505603985056,"tickwidth":0.33208800332088,"showticklabels":true,"tickfont":{"color":"rgba(77,77,77,1)","family":"","size":12.7521793275218},"tickangle":-0,"showline":false,"linecolor":null,"linewidth":0,"showgrid":true,"domain":[0,1],"gridcolor":"rgba(217,217,217,1)","gridwidth":0.33208800332088,"zeroline":false,"anchor":"y","title":"","titlefont":{"color":"rgba(0,0,0,1)","family":"","size":15.9402241594022},"hoverformat":".2f"},"yaxis":{"type":"linear","autorange":false,"tickmode":"array","range":[-1217.35,54010.35],"ticktext":["0","10,000","20,000","30,000","40,000","50,000"],"tickvals":[0,10000,20000,30000,40000,50000],"ticks":"outside","tickcolor":"rgba(179,179,179,1)","ticklen":3.98505603985056,"tickwidth":0.33208800332088,"showticklabels":true,"tickfont":{"color":"rgba(77,77,77,1)","family":"","size":12.7521793275218},"tickangle":-0,"showline":false,"linecolor":null,"linewidth":0,"showgrid":true,"domain":[0,1],"gridcolor":"rgba(217,217,217,1)","gridwidth":0.33208800332088,"zeroline":false,"anchor":"x","title":"Approximate total number of emails","titlefont":{"color":"rgba(0,0,0,1)","family":"","size":15.9402241594022},"hoverformat":".2f"},"shapes":[{"type":"rect","fillcolor":"transparent","line":{"color":"rgba(179,179,179,1)","width":0.66417600664176,"linetype":"solid"},"yref":"paper","xref":"paper","x0":0,"x1":1,"y0":0,"y1":1}],"showlegend":true,"legend":{"bgcolor":"rgba(255,255,255,1)","bordercolor":"transparent","borderwidth":1.88976377952756,"font":{"color":"rgba(0,0,0,1)","family":"","size":12.7521793275218},"y":1},"hovermode":"closest"},"source":"A","config":{"modeBarButtonsToRemove":["sendDataToCloud"]},"base_url":"https://plot.ly"},"evals":[],"jsHooks":[]}</script><!--/html_preserve-->

## Timeline of survey responses


```r
survey.orgs <- readRDS(file.path(PROJHOME, "Data", "data_processed", 
                                 "survey_orgs.rds"))

survey.time.plot <- survey.orgs %>%
  select(EndDate) %>%
  arrange(EndDate) %>%
  mutate(done = 1,
         num.completed.cum = cumsum(done))

plot.responses.timeline <- ggplot() + 
  geom_step(data=survey.time.plot,
            aes(x=EndDate, y=num.completed.cum),
            size=0.5, colour="grey50") + 
  scale_y_continuous(labels=comma) +
  scale_x_datetime(date_labels="%B %e", date_breaks="1 week") +
  guides(fill=FALSE, colour=guide_legend(title=NULL)) +
  labs(x=NULL, y="Cumulative number of responses") +
  theme_light()

plot.responses.timeline.static <- plot.responses.timeline +
  geom_vline(data=sending.groups.plot, 
             aes(xintercept=as.numeric(email_day), 
                 colour=email_type),
             size=0.5) + 
  geom_label_repel(data=sending.groups.plot,
                   aes(x=email_day, y=400, 
                       label=group_names, fill=email_type),
                   size=2.5, colour="white") +
  theme(legend.position="bottom", 
        legend.key.size=unit(0.65, "lines"),
        legend.key=element_blank(),
        panel.grid.minor=element_blank())

plot.responses.timeline.interactive <- plot.responses.timeline +
  geom_vline(data=sending.groups.plot, 
             aes(xintercept=as.numeric(email_day), 
                 colour=email_type, text=group_names),
             size=0.5)

ggplotly(plot.responses.timeline.interactive)
```

<!--html_preserve--><div id="htmlwidget-1001" style="width:672px;height:480px;" class="plotly html-widget"></div>
<script type="application/json" data-for="htmlwidget-1001">{"x":{"data":[{"x":[1461175205,1461178013,1461178218,1461179934,1461188367,1461191621,1461193969,1461198809,1461208238,1461208973,1461220382,1461222746,1461232926,1461238929,1461240578,1461241221,1461249469,1461253467,1461256412,1461257446,1461259492,1461261365,1461263247,1461266777,1461267859,1461272024,1461277983,1461285841,1461288655,1461292369,1461296570,1461300020,1461302433,1461305921,1461306744,1461309322,1461313975,1461316204,1461320094,1461323255,1461325215,1461326441,1461329790,1461335646,1461337055,1461337092,1461337270,1461337925,1461340114,1461344149,1461356158,1461362601,1461364525,1461366567,1461370255,1461376829,1461379596,1461395425,1461403583,1461420578,1461420669,1461423681,1461424860,1461429365,1461437253,1461532853,1461536263,1461553728,1461559483,1461559577,1461560532,1461566049,1461566552,1461567666,1461578388,1461586581,1461587349,1461589707,1461594094,1461603614,1461604125,1461604500,1461604834,1461629491,1461641026,1461642570,1461646792,1461652953,1461657730,1461662133,1461667994,1461671605,1461679331,1461679386,1461705046,1461724227,1461724505,1461734541,1461746925,1461749295,1461761978,1461781438,1461797893,1461798488,1461831800,1461840757,1461841224,1461848617,1461850206,1461850734,1461851198,1461851524,1461851532,1461852730,1461852948,1461854870,1461857189,1461859929,1461860786,1461866342,1461869824,1461877983,1461883030,1461885288,1461886318,1461889850,1461892140,1461894372,1461901329,1461918711,1461919553,1461924939,1461933163,1461935224,1461936032,1461938423,1461939772,1461945035,1461965136,1461969284,1461987537,1461994578,1461996857,1461997522,1461998286,1462003949,1462004313,1462016851,1462017314,1462018299,1462035675,1462054141,1462087016,1462089015,1462094253,1462095244,1462105848,1462112661,1462149451,1462161318,1462166046,1462174836,1462183302,1462185559,1462186933,1462187077,1462187101,1462187370,1462187680,1462187868,1462189331,1462189479,1462189781,1462189806,1462190302,1462190640,1462190861,1462191238,1462191439,1462191503,1462191702,1462192090,1462192356,1462192421,1462192542,1462192542,1462192564,1462192769,1462192777,1462193008,1462193047,1462193206,1462193753,1462193876,1462194291,1462194292,1462194754,1462194836,1462195237,1462195776,1462195825,1462195829,1462196354,1462196511,1462197483,1462197984,1462199014,1462199064,1462199389,1462199634,1462199731,1462199746,1462200040,1462200178,1462201239,1462201716,1462201868,1462202203,1462202402,1462203158,1462205310,1462205493,1462205919,1462205956,1462206186,1462206916,1462207112,1462207934,1462208100,1462211100,1462214042,1462216349,1462218086,1462222440,1462224880,1462225139,1462228153,1462232027,1462232525,1462234505,1462234517,1462238513,1462239764,1462244072,1462245292,1462246884,1462248226,1462249277,1462249493,1462250969,1462251267,1462252448,1462253452,1462255556,1462257460,1462259084,1462259502,1462261448,1462262087,1462262139,1462266009,1462267305,1462267388,1462268152,1462269286,1462270030,1462270337,1462270605,1462270770,1462271175,1462271354,1462271536,1462271863,1462272050,1462273395,1462275552,1462275810,1462276153,1462276446,1462277854,1462278232,1462280208,1462280857,1462285365,1462287776,1462289645,1462289897,1462290008,1462290665,1462291184,1462291299,1462291519,1462291847,1462291976,1462293577,1462296206,1462297322,1462301526,1462304126,1462306004,1462309545,1462320300,1462322313,1462322585,1462324224,1462324689,1462326208,1462326620,1462328748,1462332386,1462334691,1462335556,1462339644,1462342492,1462342964,1462346319,1462347187,1462352677,1462353203,1462353843,1462359772,1462360028,1462360576,1462361236,1462363467,1462363752,1462364851,1462371890,1462372219,1462378099,1462378281,1462382079,1462384728,1462387322,1462399606,1462401821,1462410599,1462426318,1462433000,1462434744,1462436425,1462440282,1462447626,1462451394,1462451875,1462454654,1462455824,1462457718,1462462280,1462476076,1462478558,1462479040,1462480532,1462527906,1462528064,1462532840,1462573492,1462627518,1462636046,1462659219,1462672167,1462704573,1462709259,1462767323,1462780559,1462784134,1462789253,1462813022,1462827787,1462846821,1462848818,1462855470,1462857441,1462870299,1462870698,1462873730,1462874366,1462875631,1462876436,1462877268,1462879201,1462879207,1462879424,1462879494,1462880868,1462881885,1462882166,1462882736,1462883241,1462884809,1462885512,1462885553,1462885852,1462885954,1462887775,1462893083,1462893110,1462894319,1462894704,1462896034,1462897444,1462897783,1462898098,1462898448,1462899163,1462899470,1462904543,1462905196,1462907181,1462907438,1462915755,1462917076,1462917272,1462917375,1462919382,1462921682,1462932169,1462933247,1462934774,1462936758,1462939296,1462939303,1462940055,1462941614,1462942180,1462943634,1462943897,1462947284,1462948216,1462949290,1462950096,1462951353,1462953886,1462954070,1462954116,1462954945,1462958633,1462962298,1462965404,1462967697,1462967819,1462969197,1462971455,1462971485,1462972002,1462973323,1462979602,1462981708,1462983063,1462989722,1462992881,1462996533,1463004659,1463006258,1463020211,1463025183,1463025883,1463027015,1463036625,1463037955,1463040956,1463057064,1463060739,1463063099,1463064000,1463068090,1463082896,1463088922,1463089804,1463120075,1463121737,1463123177,1463128443,1463130908,1463136335,1463147273,1463153312,1463153986,1463224906,1463287280,1463297327,1463297704,1463300250,1463306845,1463330241,1463359043,1463373528,1463399950,1463407396,1463465392,1463468270,1463475144,1463475311,1463487531,1463499915,1463542712,1463549827,1463558017,1463564666,1463573721,1463585082,1463599008,1463631857,1463674077,1463750047,1463988961,1464133638,1464239046,1464753080,1465230055,1465230067,1465230488,1465230875,1465231150,1465232657,1465233911,1465233970,1465235635,1465236134,1465238142,1465238499,1465240190,1465241740,1465244792,1465247321,1465248196,1465253084,1465268764,1465269517,1465270624,1465272420,1465274860,1465278025,1465278569,1465278940,1465280339,1465280840,1465281898,1465282582,1465282789,1465284675,1465285457,1465291095,1465294293,1465294999,1465301729,1465305147,1465305827,1465308962,1465310007,1465321276,1465326792,1465332195,1465337737,1465338551,1465339924,1465344172,1465351918,1465359234,1465367306,1465377781,1465381370,1465381678,1465384850,1465387123],"y":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,441,442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461,462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477,478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500,501,502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,539,540,541,542,543,544,545,546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562,563,564,565],"text":["EndDate: 2016-04-20 14:00:05<br>num.completed.cum: 1","EndDate: 2016-04-20 14:46:53<br>num.completed.cum: 2","EndDate: 2016-04-20 14:50:18<br>num.completed.cum: 3","EndDate: 2016-04-20 15:18:54<br>num.completed.cum: 4","EndDate: 2016-04-20 17:39:27<br>num.completed.cum: 5","EndDate: 2016-04-20 18:33:41<br>num.completed.cum: 6","EndDate: 2016-04-20 19:12:49<br>num.completed.cum: 7","EndDate: 2016-04-20 20:33:29<br>num.completed.cum: 8","EndDate: 2016-04-20 23:10:38<br>num.completed.cum: 9","EndDate: 2016-04-20 23:22:53<br>num.completed.cum: 10","EndDate: 2016-04-21 02:33:02<br>num.completed.cum: 11","EndDate: 2016-04-21 03:12:26<br>num.completed.cum: 12","EndDate: 2016-04-21 06:02:06<br>num.completed.cum: 13","EndDate: 2016-04-21 07:42:09<br>num.completed.cum: 14","EndDate: 2016-04-21 08:09:38<br>num.completed.cum: 15","EndDate: 2016-04-21 08:20:21<br>num.completed.cum: 16","EndDate: 2016-04-21 10:37:49<br>num.completed.cum: 17","EndDate: 2016-04-21 11:44:27<br>num.completed.cum: 18","EndDate: 2016-04-21 12:33:32<br>num.completed.cum: 19","EndDate: 2016-04-21 12:50:46<br>num.completed.cum: 20","EndDate: 2016-04-21 13:24:52<br>num.completed.cum: 21","EndDate: 2016-04-21 13:56:05<br>num.completed.cum: 22","EndDate: 2016-04-21 14:27:27<br>num.completed.cum: 23","EndDate: 2016-04-21 15:26:17<br>num.completed.cum: 24","EndDate: 2016-04-21 15:44:19<br>num.completed.cum: 25","EndDate: 2016-04-21 16:53:44<br>num.completed.cum: 26","EndDate: 2016-04-21 18:33:03<br>num.completed.cum: 27","EndDate: 2016-04-21 20:44:01<br>num.completed.cum: 28","EndDate: 2016-04-21 21:30:55<br>num.completed.cum: 29","EndDate: 2016-04-21 22:32:49<br>num.completed.cum: 30","EndDate: 2016-04-21 23:42:50<br>num.completed.cum: 31","EndDate: 2016-04-22 00:40:20<br>num.completed.cum: 32","EndDate: 2016-04-22 01:20:33<br>num.completed.cum: 33","EndDate: 2016-04-22 02:18:41<br>num.completed.cum: 34","EndDate: 2016-04-22 02:32:24<br>num.completed.cum: 35","EndDate: 2016-04-22 03:15:22<br>num.completed.cum: 36","EndDate: 2016-04-22 04:32:55<br>num.completed.cum: 37","EndDate: 2016-04-22 05:10:04<br>num.completed.cum: 38","EndDate: 2016-04-22 06:14:54<br>num.completed.cum: 39","EndDate: 2016-04-22 07:07:35<br>num.completed.cum: 40","EndDate: 2016-04-22 07:40:15<br>num.completed.cum: 41","EndDate: 2016-04-22 08:00:41<br>num.completed.cum: 42","EndDate: 2016-04-22 08:56:30<br>num.completed.cum: 43","EndDate: 2016-04-22 10:34:06<br>num.completed.cum: 44","EndDate: 2016-04-22 10:57:35<br>num.completed.cum: 45","EndDate: 2016-04-22 10:58:12<br>num.completed.cum: 46","EndDate: 2016-04-22 11:01:10<br>num.completed.cum: 47","EndDate: 2016-04-22 11:12:05<br>num.completed.cum: 48","EndDate: 2016-04-22 11:48:34<br>num.completed.cum: 49","EndDate: 2016-04-22 12:55:49<br>num.completed.cum: 50","EndDate: 2016-04-22 16:15:58<br>num.completed.cum: 51","EndDate: 2016-04-22 18:03:21<br>num.completed.cum: 52","EndDate: 2016-04-22 18:35:25<br>num.completed.cum: 53","EndDate: 2016-04-22 19:09:27<br>num.completed.cum: 54","EndDate: 2016-04-22 20:10:55<br>num.completed.cum: 55","EndDate: 2016-04-22 22:00:29<br>num.completed.cum: 56","EndDate: 2016-04-22 22:46:36<br>num.completed.cum: 57","EndDate: 2016-04-23 03:10:25<br>num.completed.cum: 58","EndDate: 2016-04-23 05:26:23<br>num.completed.cum: 59","EndDate: 2016-04-23 10:09:38<br>num.completed.cum: 60","EndDate: 2016-04-23 10:11:09<br>num.completed.cum: 61","EndDate: 2016-04-23 11:01:21<br>num.completed.cum: 62","EndDate: 2016-04-23 11:21:00<br>num.completed.cum: 63","EndDate: 2016-04-23 12:36:05<br>num.completed.cum: 64","EndDate: 2016-04-23 14:47:33<br>num.completed.cum: 65","EndDate: 2016-04-24 17:20:53<br>num.completed.cum: 66","EndDate: 2016-04-24 18:17:43<br>num.completed.cum: 67","EndDate: 2016-04-24 23:08:48<br>num.completed.cum: 68","EndDate: 2016-04-25 00:44:43<br>num.completed.cum: 69","EndDate: 2016-04-25 00:46:17<br>num.completed.cum: 70","EndDate: 2016-04-25 01:02:12<br>num.completed.cum: 71","EndDate: 2016-04-25 02:34:09<br>num.completed.cum: 72","EndDate: 2016-04-25 02:42:32<br>num.completed.cum: 73","EndDate: 2016-04-25 03:01:06<br>num.completed.cum: 74","EndDate: 2016-04-25 05:59:48<br>num.completed.cum: 75","EndDate: 2016-04-25 08:16:21<br>num.completed.cum: 76","EndDate: 2016-04-25 08:29:09<br>num.completed.cum: 77","EndDate: 2016-04-25 09:08:27<br>num.completed.cum: 78","EndDate: 2016-04-25 10:21:34<br>num.completed.cum: 79","EndDate: 2016-04-25 13:00:14<br>num.completed.cum: 80","EndDate: 2016-04-25 13:08:45<br>num.completed.cum: 81","EndDate: 2016-04-25 13:15:00<br>num.completed.cum: 82","EndDate: 2016-04-25 13:20:34<br>num.completed.cum: 83","EndDate: 2016-04-25 20:11:31<br>num.completed.cum: 84","EndDate: 2016-04-25 23:23:46<br>num.completed.cum: 85","EndDate: 2016-04-25 23:49:30<br>num.completed.cum: 86","EndDate: 2016-04-26 00:59:52<br>num.completed.cum: 87","EndDate: 2016-04-26 02:42:33<br>num.completed.cum: 88","EndDate: 2016-04-26 04:02:10<br>num.completed.cum: 89","EndDate: 2016-04-26 05:15:33<br>num.completed.cum: 90","EndDate: 2016-04-26 06:53:14<br>num.completed.cum: 91","EndDate: 2016-04-26 07:53:25<br>num.completed.cum: 92","EndDate: 2016-04-26 10:02:11<br>num.completed.cum: 93","EndDate: 2016-04-26 10:03:06<br>num.completed.cum: 94","EndDate: 2016-04-26 17:10:46<br>num.completed.cum: 95","EndDate: 2016-04-26 22:30:27<br>num.completed.cum: 96","EndDate: 2016-04-26 22:35:05<br>num.completed.cum: 97","EndDate: 2016-04-27 01:22:21<br>num.completed.cum: 98","EndDate: 2016-04-27 04:48:45<br>num.completed.cum: 99","EndDate: 2016-04-27 05:28:15<br>num.completed.cum: 100","EndDate: 2016-04-27 08:59:38<br>num.completed.cum: 101","EndDate: 2016-04-27 14:23:58<br>num.completed.cum: 102","EndDate: 2016-04-27 18:58:13<br>num.completed.cum: 103","EndDate: 2016-04-27 19:08:08<br>num.completed.cum: 104","EndDate: 2016-04-28 04:23:20<br>num.completed.cum: 105","EndDate: 2016-04-28 06:52:37<br>num.completed.cum: 106","EndDate: 2016-04-28 07:00:24<br>num.completed.cum: 107","EndDate: 2016-04-28 09:03:37<br>num.completed.cum: 108","EndDate: 2016-04-28 09:30:06<br>num.completed.cum: 109","EndDate: 2016-04-28 09:38:54<br>num.completed.cum: 110","EndDate: 2016-04-28 09:46:38<br>num.completed.cum: 111","EndDate: 2016-04-28 09:52:04<br>num.completed.cum: 112","EndDate: 2016-04-28 09:52:12<br>num.completed.cum: 113","EndDate: 2016-04-28 10:12:10<br>num.completed.cum: 114","EndDate: 2016-04-28 10:15:48<br>num.completed.cum: 115","EndDate: 2016-04-28 10:47:50<br>num.completed.cum: 116","EndDate: 2016-04-28 11:26:29<br>num.completed.cum: 117","EndDate: 2016-04-28 12:12:09<br>num.completed.cum: 118","EndDate: 2016-04-28 12:26:26<br>num.completed.cum: 119","EndDate: 2016-04-28 13:59:02<br>num.completed.cum: 120","EndDate: 2016-04-28 14:57:04<br>num.completed.cum: 121","EndDate: 2016-04-28 17:13:03<br>num.completed.cum: 122","EndDate: 2016-04-28 18:37:10<br>num.completed.cum: 123","EndDate: 2016-04-28 19:14:48<br>num.completed.cum: 124","EndDate: 2016-04-28 19:31:58<br>num.completed.cum: 125","EndDate: 2016-04-28 20:30:50<br>num.completed.cum: 126","EndDate: 2016-04-28 21:09:00<br>num.completed.cum: 127","EndDate: 2016-04-28 21:46:12<br>num.completed.cum: 128","EndDate: 2016-04-28 23:42:09<br>num.completed.cum: 129","EndDate: 2016-04-29 04:31:51<br>num.completed.cum: 130","EndDate: 2016-04-29 04:45:53<br>num.completed.cum: 131","EndDate: 2016-04-29 06:15:39<br>num.completed.cum: 132","EndDate: 2016-04-29 08:32:43<br>num.completed.cum: 133","EndDate: 2016-04-29 09:07:04<br>num.completed.cum: 134","EndDate: 2016-04-29 09:20:32<br>num.completed.cum: 135","EndDate: 2016-04-29 10:00:23<br>num.completed.cum: 136","EndDate: 2016-04-29 10:22:52<br>num.completed.cum: 137","EndDate: 2016-04-29 11:50:35<br>num.completed.cum: 138","EndDate: 2016-04-29 17:25:36<br>num.completed.cum: 139","EndDate: 2016-04-29 18:34:44<br>num.completed.cum: 140","EndDate: 2016-04-29 23:38:57<br>num.completed.cum: 141","EndDate: 2016-04-30 01:36:18<br>num.completed.cum: 142","EndDate: 2016-04-30 02:14:17<br>num.completed.cum: 143","EndDate: 2016-04-30 02:25:22<br>num.completed.cum: 144","EndDate: 2016-04-30 02:38:06<br>num.completed.cum: 145","EndDate: 2016-04-30 04:12:29<br>num.completed.cum: 146","EndDate: 2016-04-30 04:18:33<br>num.completed.cum: 147","EndDate: 2016-04-30 07:47:31<br>num.completed.cum: 148","EndDate: 2016-04-30 07:55:14<br>num.completed.cum: 149","EndDate: 2016-04-30 08:11:39<br>num.completed.cum: 150","EndDate: 2016-04-30 13:01:15<br>num.completed.cum: 151","EndDate: 2016-04-30 18:09:01<br>num.completed.cum: 152","EndDate: 2016-05-01 03:16:56<br>num.completed.cum: 153","EndDate: 2016-05-01 03:50:15<br>num.completed.cum: 154","EndDate: 2016-05-01 05:17:33<br>num.completed.cum: 155","EndDate: 2016-05-01 05:34:04<br>num.completed.cum: 156","EndDate: 2016-05-01 08:30:48<br>num.completed.cum: 157","EndDate: 2016-05-01 10:24:21<br>num.completed.cum: 158","EndDate: 2016-05-01 20:37:31<br>num.completed.cum: 159","EndDate: 2016-05-01 23:55:18<br>num.completed.cum: 160","EndDate: 2016-05-02 01:14:06<br>num.completed.cum: 161","EndDate: 2016-05-02 03:40:36<br>num.completed.cum: 162","EndDate: 2016-05-02 06:01:42<br>num.completed.cum: 163","EndDate: 2016-05-02 06:39:19<br>num.completed.cum: 164","EndDate: 2016-05-02 07:02:13<br>num.completed.cum: 165","EndDate: 2016-05-02 07:04:37<br>num.completed.cum: 166","EndDate: 2016-05-02 07:05:01<br>num.completed.cum: 167","EndDate: 2016-05-02 07:09:30<br>num.completed.cum: 168","EndDate: 2016-05-02 07:14:40<br>num.completed.cum: 169","EndDate: 2016-05-02 07:17:48<br>num.completed.cum: 170","EndDate: 2016-05-02 07:42:11<br>num.completed.cum: 171","EndDate: 2016-05-02 07:44:39<br>num.completed.cum: 172","EndDate: 2016-05-02 07:49:41<br>num.completed.cum: 173","EndDate: 2016-05-02 07:50:06<br>num.completed.cum: 174","EndDate: 2016-05-02 07:58:22<br>num.completed.cum: 175","EndDate: 2016-05-02 08:04:00<br>num.completed.cum: 176","EndDate: 2016-05-02 08:07:41<br>num.completed.cum: 177","EndDate: 2016-05-02 08:13:58<br>num.completed.cum: 178","EndDate: 2016-05-02 08:17:19<br>num.completed.cum: 179","EndDate: 2016-05-02 08:18:23<br>num.completed.cum: 180","EndDate: 2016-05-02 08:21:42<br>num.completed.cum: 181","EndDate: 2016-05-02 08:28:10<br>num.completed.cum: 182","EndDate: 2016-05-02 08:32:36<br>num.completed.cum: 183","EndDate: 2016-05-02 08:33:41<br>num.completed.cum: 184","EndDate: 2016-05-02 08:35:42<br>num.completed.cum: 185","EndDate: 2016-05-02 08:35:42<br>num.completed.cum: 186","EndDate: 2016-05-02 08:36:04<br>num.completed.cum: 187","EndDate: 2016-05-02 08:39:29<br>num.completed.cum: 188","EndDate: 2016-05-02 08:39:37<br>num.completed.cum: 189","EndDate: 2016-05-02 08:43:28<br>num.completed.cum: 190","EndDate: 2016-05-02 08:44:07<br>num.completed.cum: 191","EndDate: 2016-05-02 08:46:46<br>num.completed.cum: 192","EndDate: 2016-05-02 08:55:53<br>num.completed.cum: 193","EndDate: 2016-05-02 08:57:56<br>num.completed.cum: 194","EndDate: 2016-05-02 09:04:51<br>num.completed.cum: 195","EndDate: 2016-05-02 09:04:52<br>num.completed.cum: 196","EndDate: 2016-05-02 09:12:34<br>num.completed.cum: 197","EndDate: 2016-05-02 09:13:56<br>num.completed.cum: 198","EndDate: 2016-05-02 09:20:37<br>num.completed.cum: 199","EndDate: 2016-05-02 09:29:36<br>num.completed.cum: 200","EndDate: 2016-05-02 09:30:25<br>num.completed.cum: 201","EndDate: 2016-05-02 09:30:29<br>num.completed.cum: 202","EndDate: 2016-05-02 09:39:14<br>num.completed.cum: 203","EndDate: 2016-05-02 09:41:51<br>num.completed.cum: 204","EndDate: 2016-05-02 09:58:03<br>num.completed.cum: 205","EndDate: 2016-05-02 10:06:24<br>num.completed.cum: 206","EndDate: 2016-05-02 10:23:34<br>num.completed.cum: 207","EndDate: 2016-05-02 10:24:24<br>num.completed.cum: 208","EndDate: 2016-05-02 10:29:49<br>num.completed.cum: 209","EndDate: 2016-05-02 10:33:54<br>num.completed.cum: 210","EndDate: 2016-05-02 10:35:31<br>num.completed.cum: 211","EndDate: 2016-05-02 10:35:46<br>num.completed.cum: 212","EndDate: 2016-05-02 10:40:40<br>num.completed.cum: 213","EndDate: 2016-05-02 10:42:58<br>num.completed.cum: 214","EndDate: 2016-05-02 11:00:39<br>num.completed.cum: 215","EndDate: 2016-05-02 11:08:36<br>num.completed.cum: 216","EndDate: 2016-05-02 11:11:08<br>num.completed.cum: 217","EndDate: 2016-05-02 11:16:43<br>num.completed.cum: 218","EndDate: 2016-05-02 11:20:02<br>num.completed.cum: 219","EndDate: 2016-05-02 11:32:38<br>num.completed.cum: 220","EndDate: 2016-05-02 12:08:30<br>num.completed.cum: 221","EndDate: 2016-05-02 12:11:33<br>num.completed.cum: 222","EndDate: 2016-05-02 12:18:39<br>num.completed.cum: 223","EndDate: 2016-05-02 12:19:16<br>num.completed.cum: 224","EndDate: 2016-05-02 12:23:06<br>num.completed.cum: 225","EndDate: 2016-05-02 12:35:16<br>num.completed.cum: 226","EndDate: 2016-05-02 12:38:32<br>num.completed.cum: 227","EndDate: 2016-05-02 12:52:14<br>num.completed.cum: 228","EndDate: 2016-05-02 12:55:00<br>num.completed.cum: 229","EndDate: 2016-05-02 13:45:00<br>num.completed.cum: 230","EndDate: 2016-05-02 14:34:02<br>num.completed.cum: 231","EndDate: 2016-05-02 15:12:29<br>num.completed.cum: 232","EndDate: 2016-05-02 15:41:26<br>num.completed.cum: 233","EndDate: 2016-05-02 16:54:00<br>num.completed.cum: 234","EndDate: 2016-05-02 17:34:40<br>num.completed.cum: 235","EndDate: 2016-05-02 17:38:59<br>num.completed.cum: 236","EndDate: 2016-05-02 18:29:13<br>num.completed.cum: 237","EndDate: 2016-05-02 19:33:47<br>num.completed.cum: 238","EndDate: 2016-05-02 19:42:05<br>num.completed.cum: 239","EndDate: 2016-05-02 20:15:05<br>num.completed.cum: 240","EndDate: 2016-05-02 20:15:17<br>num.completed.cum: 241","EndDate: 2016-05-02 21:21:53<br>num.completed.cum: 242","EndDate: 2016-05-02 21:42:44<br>num.completed.cum: 243","EndDate: 2016-05-02 22:54:32<br>num.completed.cum: 244","EndDate: 2016-05-02 23:14:52<br>num.completed.cum: 245","EndDate: 2016-05-02 23:41:24<br>num.completed.cum: 246","EndDate: 2016-05-03 00:03:46<br>num.completed.cum: 247","EndDate: 2016-05-03 00:21:17<br>num.completed.cum: 248","EndDate: 2016-05-03 00:24:53<br>num.completed.cum: 249","EndDate: 2016-05-03 00:49:29<br>num.completed.cum: 250","EndDate: 2016-05-03 00:54:27<br>num.completed.cum: 251","EndDate: 2016-05-03 01:14:08<br>num.completed.cum: 252","EndDate: 2016-05-03 01:30:52<br>num.completed.cum: 253","EndDate: 2016-05-03 02:05:56<br>num.completed.cum: 254","EndDate: 2016-05-03 02:37:40<br>num.completed.cum: 255","EndDate: 2016-05-03 03:04:44<br>num.completed.cum: 256","EndDate: 2016-05-03 03:11:42<br>num.completed.cum: 257","EndDate: 2016-05-03 03:44:08<br>num.completed.cum: 258","EndDate: 2016-05-03 03:54:47<br>num.completed.cum: 259","EndDate: 2016-05-03 03:55:39<br>num.completed.cum: 260","EndDate: 2016-05-03 05:00:09<br>num.completed.cum: 261","EndDate: 2016-05-03 05:21:45<br>num.completed.cum: 262","EndDate: 2016-05-03 05:23:08<br>num.completed.cum: 263","EndDate: 2016-05-03 05:35:52<br>num.completed.cum: 264","EndDate: 2016-05-03 05:54:46<br>num.completed.cum: 265","EndDate: 2016-05-03 06:07:10<br>num.completed.cum: 266","EndDate: 2016-05-03 06:12:17<br>num.completed.cum: 267","EndDate: 2016-05-03 06:16:45<br>num.completed.cum: 268","EndDate: 2016-05-03 06:19:30<br>num.completed.cum: 269","EndDate: 2016-05-03 06:26:15<br>num.completed.cum: 270","EndDate: 2016-05-03 06:29:14<br>num.completed.cum: 271","EndDate: 2016-05-03 06:32:16<br>num.completed.cum: 272","EndDate: 2016-05-03 06:37:43<br>num.completed.cum: 273","EndDate: 2016-05-03 06:40:50<br>num.completed.cum: 274","EndDate: 2016-05-03 07:03:15<br>num.completed.cum: 275","EndDate: 2016-05-03 07:39:12<br>num.completed.cum: 276","EndDate: 2016-05-03 07:43:30<br>num.completed.cum: 277","EndDate: 2016-05-03 07:49:13<br>num.completed.cum: 278","EndDate: 2016-05-03 07:54:06<br>num.completed.cum: 279","EndDate: 2016-05-03 08:17:34<br>num.completed.cum: 280","EndDate: 2016-05-03 08:23:52<br>num.completed.cum: 281","EndDate: 2016-05-03 08:56:48<br>num.completed.cum: 282","EndDate: 2016-05-03 09:07:37<br>num.completed.cum: 283","EndDate: 2016-05-03 10:22:45<br>num.completed.cum: 284","EndDate: 2016-05-03 11:02:56<br>num.completed.cum: 285","EndDate: 2016-05-03 11:34:05<br>num.completed.cum: 286","EndDate: 2016-05-03 11:38:17<br>num.completed.cum: 287","EndDate: 2016-05-03 11:40:08<br>num.completed.cum: 288","EndDate: 2016-05-03 11:51:05<br>num.completed.cum: 289","EndDate: 2016-05-03 11:59:44<br>num.completed.cum: 290","EndDate: 2016-05-03 12:01:39<br>num.completed.cum: 291","EndDate: 2016-05-03 12:05:19<br>num.completed.cum: 292","EndDate: 2016-05-03 12:10:47<br>num.completed.cum: 293","EndDate: 2016-05-03 12:12:56<br>num.completed.cum: 294","EndDate: 2016-05-03 12:39:37<br>num.completed.cum: 295","EndDate: 2016-05-03 13:23:26<br>num.completed.cum: 296","EndDate: 2016-05-03 13:42:02<br>num.completed.cum: 297","EndDate: 2016-05-03 14:52:06<br>num.completed.cum: 298","EndDate: 2016-05-03 15:35:26<br>num.completed.cum: 299","EndDate: 2016-05-03 16:06:44<br>num.completed.cum: 300","EndDate: 2016-05-03 17:05:45<br>num.completed.cum: 301","EndDate: 2016-05-03 20:05:00<br>num.completed.cum: 302","EndDate: 2016-05-03 20:38:33<br>num.completed.cum: 303","EndDate: 2016-05-03 20:43:05<br>num.completed.cum: 304","EndDate: 2016-05-03 21:10:24<br>num.completed.cum: 305","EndDate: 2016-05-03 21:18:09<br>num.completed.cum: 306","EndDate: 2016-05-03 21:43:28<br>num.completed.cum: 307","EndDate: 2016-05-03 21:50:20<br>num.completed.cum: 308","EndDate: 2016-05-03 22:25:48<br>num.completed.cum: 309","EndDate: 2016-05-03 23:26:26<br>num.completed.cum: 310","EndDate: 2016-05-04 00:04:51<br>num.completed.cum: 311","EndDate: 2016-05-04 00:19:16<br>num.completed.cum: 312","EndDate: 2016-05-04 01:27:24<br>num.completed.cum: 313","EndDate: 2016-05-04 02:14:52<br>num.completed.cum: 314","EndDate: 2016-05-04 02:22:44<br>num.completed.cum: 315","EndDate: 2016-05-04 03:18:39<br>num.completed.cum: 316","EndDate: 2016-05-04 03:33:07<br>num.completed.cum: 317","EndDate: 2016-05-04 05:04:37<br>num.completed.cum: 318","EndDate: 2016-05-04 05:13:23<br>num.completed.cum: 319","EndDate: 2016-05-04 05:24:03<br>num.completed.cum: 320","EndDate: 2016-05-04 07:02:52<br>num.completed.cum: 321","EndDate: 2016-05-04 07:07:08<br>num.completed.cum: 322","EndDate: 2016-05-04 07:16:16<br>num.completed.cum: 323","EndDate: 2016-05-04 07:27:16<br>num.completed.cum: 324","EndDate: 2016-05-04 08:04:27<br>num.completed.cum: 325","EndDate: 2016-05-04 08:09:12<br>num.completed.cum: 326","EndDate: 2016-05-04 08:27:31<br>num.completed.cum: 327","EndDate: 2016-05-04 10:24:50<br>num.completed.cum: 328","EndDate: 2016-05-04 10:30:19<br>num.completed.cum: 329","EndDate: 2016-05-04 12:08:19<br>num.completed.cum: 330","EndDate: 2016-05-04 12:11:21<br>num.completed.cum: 331","EndDate: 2016-05-04 13:14:39<br>num.completed.cum: 332","EndDate: 2016-05-04 13:58:48<br>num.completed.cum: 333","EndDate: 2016-05-04 14:42:02<br>num.completed.cum: 334","EndDate: 2016-05-04 18:06:46<br>num.completed.cum: 335","EndDate: 2016-05-04 18:43:41<br>num.completed.cum: 336","EndDate: 2016-05-04 21:09:59<br>num.completed.cum: 337","EndDate: 2016-05-05 01:31:58<br>num.completed.cum: 338","EndDate: 2016-05-05 03:23:20<br>num.completed.cum: 339","EndDate: 2016-05-05 03:52:24<br>num.completed.cum: 340","EndDate: 2016-05-05 04:20:25<br>num.completed.cum: 341","EndDate: 2016-05-05 05:24:42<br>num.completed.cum: 342","EndDate: 2016-05-05 07:27:06<br>num.completed.cum: 343","EndDate: 2016-05-05 08:29:54<br>num.completed.cum: 344","EndDate: 2016-05-05 08:37:55<br>num.completed.cum: 345","EndDate: 2016-05-05 09:24:14<br>num.completed.cum: 346","EndDate: 2016-05-05 09:43:44<br>num.completed.cum: 347","EndDate: 2016-05-05 10:15:18<br>num.completed.cum: 348","EndDate: 2016-05-05 11:31:20<br>num.completed.cum: 349","EndDate: 2016-05-05 15:21:16<br>num.completed.cum: 350","EndDate: 2016-05-05 16:02:38<br>num.completed.cum: 351","EndDate: 2016-05-05 16:10:40<br>num.completed.cum: 352","EndDate: 2016-05-05 16:35:32<br>num.completed.cum: 353","EndDate: 2016-05-06 05:45:06<br>num.completed.cum: 354","EndDate: 2016-05-06 05:47:44<br>num.completed.cum: 355","EndDate: 2016-05-06 07:07:20<br>num.completed.cum: 356","EndDate: 2016-05-06 18:24:52<br>num.completed.cum: 357","EndDate: 2016-05-07 09:25:18<br>num.completed.cum: 358","EndDate: 2016-05-07 11:47:26<br>num.completed.cum: 359","EndDate: 2016-05-07 18:13:39<br>num.completed.cum: 360","EndDate: 2016-05-07 21:49:27<br>num.completed.cum: 361","EndDate: 2016-05-08 06:49:33<br>num.completed.cum: 362","EndDate: 2016-05-08 08:07:39<br>num.completed.cum: 363","EndDate: 2016-05-09 00:15:23<br>num.completed.cum: 364","EndDate: 2016-05-09 03:55:59<br>num.completed.cum: 365","EndDate: 2016-05-09 04:55:34<br>num.completed.cum: 366","EndDate: 2016-05-09 06:20:53<br>num.completed.cum: 367","EndDate: 2016-05-09 12:57:02<br>num.completed.cum: 368","EndDate: 2016-05-09 17:03:07<br>num.completed.cum: 369","EndDate: 2016-05-09 22:20:21<br>num.completed.cum: 370","EndDate: 2016-05-09 22:53:38<br>num.completed.cum: 371","EndDate: 2016-05-10 00:44:30<br>num.completed.cum: 372","EndDate: 2016-05-10 01:17:21<br>num.completed.cum: 373","EndDate: 2016-05-10 04:51:39<br>num.completed.cum: 374","EndDate: 2016-05-10 04:58:18<br>num.completed.cum: 375","EndDate: 2016-05-10 05:48:50<br>num.completed.cum: 376","EndDate: 2016-05-10 05:59:26<br>num.completed.cum: 377","EndDate: 2016-05-10 06:20:31<br>num.completed.cum: 378","EndDate: 2016-05-10 06:33:56<br>num.completed.cum: 379","EndDate: 2016-05-10 06:47:48<br>num.completed.cum: 380","EndDate: 2016-05-10 07:20:01<br>num.completed.cum: 381","EndDate: 2016-05-10 07:20:07<br>num.completed.cum: 382","EndDate: 2016-05-10 07:23:44<br>num.completed.cum: 383","EndDate: 2016-05-10 07:24:54<br>num.completed.cum: 384","EndDate: 2016-05-10 07:47:48<br>num.completed.cum: 385","EndDate: 2016-05-10 08:04:45<br>num.completed.cum: 386","EndDate: 2016-05-10 08:09:26<br>num.completed.cum: 387","EndDate: 2016-05-10 08:18:56<br>num.completed.cum: 388","EndDate: 2016-05-10 08:27:21<br>num.completed.cum: 389","EndDate: 2016-05-10 08:53:29<br>num.completed.cum: 390","EndDate: 2016-05-10 09:05:12<br>num.completed.cum: 391","EndDate: 2016-05-10 09:05:53<br>num.completed.cum: 392","EndDate: 2016-05-10 09:10:52<br>num.completed.cum: 393","EndDate: 2016-05-10 09:12:34<br>num.completed.cum: 394","EndDate: 2016-05-10 09:42:55<br>num.completed.cum: 395","EndDate: 2016-05-10 11:11:23<br>num.completed.cum: 396","EndDate: 2016-05-10 11:11:50<br>num.completed.cum: 397","EndDate: 2016-05-10 11:31:59<br>num.completed.cum: 398","EndDate: 2016-05-10 11:38:24<br>num.completed.cum: 399","EndDate: 2016-05-10 12:00:34<br>num.completed.cum: 400","EndDate: 2016-05-10 12:24:04<br>num.completed.cum: 401","EndDate: 2016-05-10 12:29:43<br>num.completed.cum: 402","EndDate: 2016-05-10 12:34:58<br>num.completed.cum: 403","EndDate: 2016-05-10 12:40:48<br>num.completed.cum: 404","EndDate: 2016-05-10 12:52:43<br>num.completed.cum: 405","EndDate: 2016-05-10 12:57:50<br>num.completed.cum: 406","EndDate: 2016-05-10 14:22:23<br>num.completed.cum: 407","EndDate: 2016-05-10 14:33:16<br>num.completed.cum: 408","EndDate: 2016-05-10 15:06:21<br>num.completed.cum: 409","EndDate: 2016-05-10 15:10:38<br>num.completed.cum: 410","EndDate: 2016-05-10 17:29:15<br>num.completed.cum: 411","EndDate: 2016-05-10 17:51:16<br>num.completed.cum: 412","EndDate: 2016-05-10 17:54:32<br>num.completed.cum: 413","EndDate: 2016-05-10 17:56:15<br>num.completed.cum: 414","EndDate: 2016-05-10 18:29:42<br>num.completed.cum: 415","EndDate: 2016-05-10 19:08:02<br>num.completed.cum: 416","EndDate: 2016-05-10 22:02:49<br>num.completed.cum: 417","EndDate: 2016-05-10 22:20:47<br>num.completed.cum: 418","EndDate: 2016-05-10 22:46:14<br>num.completed.cum: 419","EndDate: 2016-05-10 23:19:18<br>num.completed.cum: 420","EndDate: 2016-05-11 00:01:36<br>num.completed.cum: 421","EndDate: 2016-05-11 00:01:43<br>num.completed.cum: 422","EndDate: 2016-05-11 00:14:15<br>num.completed.cum: 423","EndDate: 2016-05-11 00:40:14<br>num.completed.cum: 424","EndDate: 2016-05-11 00:49:40<br>num.completed.cum: 425","EndDate: 2016-05-11 01:13:54<br>num.completed.cum: 426","EndDate: 2016-05-11 01:18:17<br>num.completed.cum: 427","EndDate: 2016-05-11 02:14:44<br>num.completed.cum: 428","EndDate: 2016-05-11 02:30:16<br>num.completed.cum: 429","EndDate: 2016-05-11 02:48:10<br>num.completed.cum: 430","EndDate: 2016-05-11 03:01:36<br>num.completed.cum: 431","EndDate: 2016-05-11 03:22:33<br>num.completed.cum: 432","EndDate: 2016-05-11 04:04:46<br>num.completed.cum: 433","EndDate: 2016-05-11 04:07:50<br>num.completed.cum: 434","EndDate: 2016-05-11 04:08:36<br>num.completed.cum: 435","EndDate: 2016-05-11 04:22:25<br>num.completed.cum: 436","EndDate: 2016-05-11 05:23:53<br>num.completed.cum: 437","EndDate: 2016-05-11 06:24:58<br>num.completed.cum: 438","EndDate: 2016-05-11 07:16:44<br>num.completed.cum: 439","EndDate: 2016-05-11 07:54:57<br>num.completed.cum: 440","EndDate: 2016-05-11 07:56:59<br>num.completed.cum: 441","EndDate: 2016-05-11 08:19:57<br>num.completed.cum: 442","EndDate: 2016-05-11 08:57:35<br>num.completed.cum: 443","EndDate: 2016-05-11 08:58:05<br>num.completed.cum: 444","EndDate: 2016-05-11 09:06:42<br>num.completed.cum: 445","EndDate: 2016-05-11 09:28:43<br>num.completed.cum: 446","EndDate: 2016-05-11 11:13:22<br>num.completed.cum: 447","EndDate: 2016-05-11 11:48:28<br>num.completed.cum: 448","EndDate: 2016-05-11 12:11:03<br>num.completed.cum: 449","EndDate: 2016-05-11 14:02:02<br>num.completed.cum: 450","EndDate: 2016-05-11 14:54:41<br>num.completed.cum: 451","EndDate: 2016-05-11 15:55:33<br>num.completed.cum: 452","EndDate: 2016-05-11 18:10:59<br>num.completed.cum: 453","EndDate: 2016-05-11 18:37:38<br>num.completed.cum: 454","EndDate: 2016-05-11 22:30:11<br>num.completed.cum: 455","EndDate: 2016-05-11 23:53:03<br>num.completed.cum: 456","EndDate: 2016-05-12 00:04:43<br>num.completed.cum: 457","EndDate: 2016-05-12 00:23:35<br>num.completed.cum: 458","EndDate: 2016-05-12 03:03:45<br>num.completed.cum: 459","EndDate: 2016-05-12 03:25:55<br>num.completed.cum: 460","EndDate: 2016-05-12 04:15:56<br>num.completed.cum: 461","EndDate: 2016-05-12 08:44:24<br>num.completed.cum: 462","EndDate: 2016-05-12 09:45:39<br>num.completed.cum: 463","EndDate: 2016-05-12 10:24:59<br>num.completed.cum: 464","EndDate: 2016-05-12 10:40:00<br>num.completed.cum: 465","EndDate: 2016-05-12 11:48:10<br>num.completed.cum: 466","EndDate: 2016-05-12 15:54:56<br>num.completed.cum: 467","EndDate: 2016-05-12 17:35:22<br>num.completed.cum: 468","EndDate: 2016-05-12 17:50:04<br>num.completed.cum: 469","EndDate: 2016-05-13 02:14:35<br>num.completed.cum: 470","EndDate: 2016-05-13 02:42:17<br>num.completed.cum: 471","EndDate: 2016-05-13 03:06:17<br>num.completed.cum: 472","EndDate: 2016-05-13 04:34:03<br>num.completed.cum: 473","EndDate: 2016-05-13 05:15:08<br>num.completed.cum: 474","EndDate: 2016-05-13 06:45:35<br>num.completed.cum: 475","EndDate: 2016-05-13 09:47:53<br>num.completed.cum: 476","EndDate: 2016-05-13 11:28:32<br>num.completed.cum: 477","EndDate: 2016-05-13 11:39:46<br>num.completed.cum: 478","EndDate: 2016-05-14 07:21:46<br>num.completed.cum: 479","EndDate: 2016-05-15 00:41:20<br>num.completed.cum: 480","EndDate: 2016-05-15 03:28:47<br>num.completed.cum: 481","EndDate: 2016-05-15 03:35:04<br>num.completed.cum: 482","EndDate: 2016-05-15 04:17:30<br>num.completed.cum: 483","EndDate: 2016-05-15 06:07:25<br>num.completed.cum: 484","EndDate: 2016-05-15 12:37:21<br>num.completed.cum: 485","EndDate: 2016-05-15 20:37:23<br>num.completed.cum: 486","EndDate: 2016-05-16 00:38:48<br>num.completed.cum: 487","EndDate: 2016-05-16 07:59:10<br>num.completed.cum: 488","EndDate: 2016-05-16 10:03:16<br>num.completed.cum: 489","EndDate: 2016-05-17 02:09:52<br>num.completed.cum: 490","EndDate: 2016-05-17 02:57:50<br>num.completed.cum: 491","EndDate: 2016-05-17 04:52:24<br>num.completed.cum: 492","EndDate: 2016-05-17 04:55:11<br>num.completed.cum: 493","EndDate: 2016-05-17 08:18:51<br>num.completed.cum: 494","EndDate: 2016-05-17 11:45:15<br>num.completed.cum: 495","EndDate: 2016-05-17 23:38:32<br>num.completed.cum: 496","EndDate: 2016-05-18 01:37:07<br>num.completed.cum: 497","EndDate: 2016-05-18 03:53:37<br>num.completed.cum: 498","EndDate: 2016-05-18 05:44:26<br>num.completed.cum: 499","EndDate: 2016-05-18 08:15:21<br>num.completed.cum: 500","EndDate: 2016-05-18 11:24:42<br>num.completed.cum: 501","EndDate: 2016-05-18 15:16:48<br>num.completed.cum: 502","EndDate: 2016-05-19 00:24:17<br>num.completed.cum: 503","EndDate: 2016-05-19 12:07:57<br>num.completed.cum: 504","EndDate: 2016-05-20 09:14:07<br>num.completed.cum: 505","EndDate: 2016-05-23 03:36:01<br>num.completed.cum: 506","EndDate: 2016-05-24 19:47:18<br>num.completed.cum: 507","EndDate: 2016-05-26 01:04:06<br>num.completed.cum: 508","EndDate: 2016-05-31 23:51:20<br>num.completed.cum: 509","EndDate: 2016-06-06 12:20:55<br>num.completed.cum: 510","EndDate: 2016-06-06 12:21:07<br>num.completed.cum: 511","EndDate: 2016-06-06 12:28:08<br>num.completed.cum: 512","EndDate: 2016-06-06 12:34:35<br>num.completed.cum: 513","EndDate: 2016-06-06 12:39:10<br>num.completed.cum: 514","EndDate: 2016-06-06 13:04:17<br>num.completed.cum: 515","EndDate: 2016-06-06 13:25:11<br>num.completed.cum: 516","EndDate: 2016-06-06 13:26:10<br>num.completed.cum: 517","EndDate: 2016-06-06 13:53:55<br>num.completed.cum: 518","EndDate: 2016-06-06 14:02:14<br>num.completed.cum: 519","EndDate: 2016-06-06 14:35:42<br>num.completed.cum: 520","EndDate: 2016-06-06 14:41:39<br>num.completed.cum: 521","EndDate: 2016-06-06 15:09:50<br>num.completed.cum: 522","EndDate: 2016-06-06 15:35:40<br>num.completed.cum: 523","EndDate: 2016-06-06 16:26:32<br>num.completed.cum: 524","EndDate: 2016-06-06 17:08:41<br>num.completed.cum: 525","EndDate: 2016-06-06 17:23:16<br>num.completed.cum: 526","EndDate: 2016-06-06 18:44:44<br>num.completed.cum: 527","EndDate: 2016-06-06 23:06:04<br>num.completed.cum: 528","EndDate: 2016-06-06 23:18:37<br>num.completed.cum: 529","EndDate: 2016-06-06 23:37:04<br>num.completed.cum: 530","EndDate: 2016-06-07 00:07:00<br>num.completed.cum: 531","EndDate: 2016-06-07 00:47:40<br>num.completed.cum: 532","EndDate: 2016-06-07 01:40:25<br>num.completed.cum: 533","EndDate: 2016-06-07 01:49:29<br>num.completed.cum: 534","EndDate: 2016-06-07 01:55:40<br>num.completed.cum: 535","EndDate: 2016-06-07 02:18:59<br>num.completed.cum: 536","EndDate: 2016-06-07 02:27:20<br>num.completed.cum: 537","EndDate: 2016-06-07 02:44:58<br>num.completed.cum: 538","EndDate: 2016-06-07 02:56:22<br>num.completed.cum: 539","EndDate: 2016-06-07 02:59:49<br>num.completed.cum: 540","EndDate: 2016-06-07 03:31:15<br>num.completed.cum: 541","EndDate: 2016-06-07 03:44:17<br>num.completed.cum: 542","EndDate: 2016-06-07 05:18:15<br>num.completed.cum: 543","EndDate: 2016-06-07 06:11:33<br>num.completed.cum: 544","EndDate: 2016-06-07 06:23:19<br>num.completed.cum: 545","EndDate: 2016-06-07 08:15:29<br>num.completed.cum: 546","EndDate: 2016-06-07 09:12:27<br>num.completed.cum: 547","EndDate: 2016-06-07 09:23:47<br>num.completed.cum: 548","EndDate: 2016-06-07 10:16:02<br>num.completed.cum: 549","EndDate: 2016-06-07 10:33:27<br>num.completed.cum: 550","EndDate: 2016-06-07 13:41:16<br>num.completed.cum: 551","EndDate: 2016-06-07 15:13:12<br>num.completed.cum: 552","EndDate: 2016-06-07 16:43:15<br>num.completed.cum: 553","EndDate: 2016-06-07 18:15:37<br>num.completed.cum: 554","EndDate: 2016-06-07 18:29:11<br>num.completed.cum: 555","EndDate: 2016-06-07 18:52:04<br>num.completed.cum: 556","EndDate: 2016-06-07 20:02:52<br>num.completed.cum: 557","EndDate: 2016-06-07 22:11:58<br>num.completed.cum: 558","EndDate: 2016-06-08 00:13:54<br>num.completed.cum: 559","EndDate: 2016-06-08 02:28:26<br>num.completed.cum: 560","EndDate: 2016-06-08 05:23:01<br>num.completed.cum: 561","EndDate: 2016-06-08 06:22:50<br>num.completed.cum: 562","EndDate: 2016-06-08 06:27:58<br>num.completed.cum: 563","EndDate: 2016-06-08 07:20:50<br>num.completed.cum: 564","EndDate: 2016-06-08 07:58:43<br>num.completed.cum: 565"],"key":null,"type":"scatter","mode":"lines","name":"","line":{"width":1.88976377952756,"color":"rgba(127,127,127,1)","dash":"solid","shape":"hv"},"showlegend":false,"xaxis":"x","yaxis":"y","hoverinfo":"text"},{"x":[1461196800,1461196800,null,1461283200,1461283200,null,1461369600,1461369600,null,1461888000,1461888000,null,1461974400,1461974400,null,1462233600,1462233600,null,1465344000,1465344000],"y":[-27.2,593.2,null,-27.2,593.2,null,-27.2,593.2,null,-27.2,593.2,null,-27.2,593.2,null,-27.2,593.2,null,-27.2,593.2],"text":["as.numeric(email_day): 1461196800<br>email_type: Invitation  <br>Groups 1-3","as.numeric(email_day): 1461196800<br>email_type: Invitation  <br>Groups 1-3","as.numeric(email_day): 1461196800<br>email_type: Invitation  <br>Groups 1-3","as.numeric(email_day): 1461283200<br>email_type: Invitation  <br>Groups 4-6","as.numeric(email_day): 1461283200<br>email_type: Invitation  <br>Groups 4-6","as.numeric(email_day): 1461283200<br>email_type: Invitation  <br>Groups 4-6","as.numeric(email_day): 1461369600<br>email_type: Invitation  <br>Groups 7-8","as.numeric(email_day): 1461369600<br>email_type: Invitation  <br>Groups 7-8","as.numeric(email_day): 1461369600<br>email_type: Invitation  <br>Groups 7-8","as.numeric(email_day): 1461888000<br>email_type: Invitation  <br>Groups 10-13","as.numeric(email_day): 1461888000<br>email_type: Invitation  <br>Groups 10-13","as.numeric(email_day): 1461888000<br>email_type: Invitation  <br>Groups 10-13","as.numeric(email_day): 1461974400<br>email_type: Invitation  <br>Groups 14-15","as.numeric(email_day): 1461974400<br>email_type: Invitation  <br>Groups 14-15","as.numeric(email_day): 1461974400<br>email_type: Invitation  <br>Groups 14-15","as.numeric(email_day): 1462233600<br>email_type: Invitation  <br>Groups 16-28","as.numeric(email_day): 1462233600<br>email_type: Invitation  <br>Groups 16-28","as.numeric(email_day): 1462233600<br>email_type: Invitation  <br>Groups 16-28","as.numeric(email_day): 1465344000<br>email_type: Invitation  <br>Group 9","as.numeric(email_day): 1465344000<br>email_type: Invitation  <br>Group 9"],"key":null,"type":"scatter","mode":"lines","name":"Invitation  ","line":{"width":1.88976377952756,"color":"rgba(248,118,109,1)","dash":"solid"},"legendgroup":"Invitation  ","showlegend":true,"xaxis":"x","yaxis":"y","hoverinfo":"text"},{"x":[1462320000,1462320000,null,1462924800,1462924800],"y":[-27.2,593.2,null,-27.2,593.2],"text":["as.numeric(email_day): 1462320000<br>email_type: Reminder  <br>Groups 1-8","as.numeric(email_day): 1462320000<br>email_type: Reminder  <br>Groups 1-8","as.numeric(email_day): 1462320000<br>email_type: Reminder  <br>Groups 1-8","as.numeric(email_day): 1462924800<br>email_type: Reminder  <br>Groups 10-28","as.numeric(email_day): 1462924800<br>email_type: Reminder  <br>Groups 10-28"],"key":null,"type":"scatter","mode":"lines","name":"Reminder  ","line":{"width":1.88976377952756,"color":"rgba(0,186,56,1)","dash":"solid"},"legendgroup":"Reminder  ","showlegend":true,"xaxis":"x","yaxis":"y","hoverinfo":"text"},{"x":[1465257600,1465257600,null,1465344000,1465344000],"y":[-27.2,593.2,null,-27.2,593.2],"text":["as.numeric(email_day): 1465257600<br>email_type: Final reminder<br>Groups 10-28","as.numeric(email_day): 1465257600<br>email_type: Final reminder<br>Groups 10-28","as.numeric(email_day): 1465257600<br>email_type: Final reminder<br>Groups 10-28","as.numeric(email_day): 1465344000<br>email_type: Final reminder<br>Groups 1-8","as.numeric(email_day): 1465344000<br>email_type: Final reminder<br>Groups 1-8"],"key":null,"type":"scatter","mode":"lines","name":"Final reminder","line":{"width":1.88976377952756,"color":"rgba(97,156,255,1)","dash":"solid"},"legendgroup":"Final reminder","showlegend":true,"xaxis":"x","yaxis":"y","hoverinfo":"text"}],"layout":{"margin":{"b":27.8953922789539,"l":47.0236612702366,"t":27.1581569115816,"r":7.97011207970112},"plot_bgcolor":"rgba(255,255,255,1)","paper_bgcolor":"rgba(255,255,255,1)","font":{"color":"rgba(0,0,0,1)","family":"","size":15.9402241594022},"xaxis":{"type":"linear","autorange":false,"tickmode":"array","range":[1460964609.1,1465597718.9],"ticktext":["April 25","May  2","May  9","May 16","May 23","May 30","June  6"],"tickvals":[1461542400,1462147200,1462752000,1463356800,1463961600,1464566400,1465171200],"ticks":"outside","tickcolor":"rgba(179,179,179,1)","ticklen":3.98505603985056,"tickwidth":0.33208800332088,"showticklabels":true,"tickfont":{"color":"rgba(77,77,77,1)","family":"","size":12.7521793275218},"tickangle":-0,"showline":false,"linecolor":null,"linewidth":0,"showgrid":true,"domain":[0,1],"gridcolor":"rgba(217,217,217,1)","gridwidth":0.33208800332088,"zeroline":false,"anchor":"y","title":"","titlefont":{"color":"rgba(0,0,0,1)","family":"","size":15.9402241594022},"hoverformat":".2f"},"yaxis":{"type":"linear","autorange":false,"tickmode":"array","range":[-27.2,593.2],"ticktext":["0","200","400"],"tickvals":[0,200,400],"ticks":"outside","tickcolor":"rgba(179,179,179,1)","ticklen":3.98505603985056,"tickwidth":0.33208800332088,"showticklabels":true,"tickfont":{"color":"rgba(77,77,77,1)","family":"","size":12.7521793275218},"tickangle":-0,"showline":false,"linecolor":null,"linewidth":0,"showgrid":true,"domain":[0,1],"gridcolor":"rgba(217,217,217,1)","gridwidth":0.33208800332088,"zeroline":false,"anchor":"x","title":"Cumulative number of responses","titlefont":{"color":"rgba(0,0,0,1)","family":"","size":15.9402241594022},"hoverformat":".2f"},"shapes":[{"type":"rect","fillcolor":"transparent","line":{"color":"rgba(179,179,179,1)","width":0.66417600664176,"linetype":"solid"},"yref":"paper","xref":"paper","x0":0,"x1":1,"y0":0,"y1":1}],"showlegend":true,"legend":{"bgcolor":"rgba(255,255,255,1)","bordercolor":"transparent","borderwidth":1.88976377952756,"font":{"color":"rgba(0,0,0,1)","family":"","size":12.7521793275218},"y":1},"hovermode":"closest"},"source":"A","config":{"modeBarButtonsToRemove":["sendDataToCloud"]},"base_url":"https://plot.ly"},"evals":[],"jsHooks":[]}</script><!--/html_preserve-->

# References


---
title: "completion_rates.R"
author: "andrew"
date: "Thu Jun  9 16:13:50 2016"
---
