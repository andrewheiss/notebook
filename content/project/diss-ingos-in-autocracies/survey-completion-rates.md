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

# Load full survey data (minus the Q4\* loop for simplicity)
survey.orgs.all <- readRDS(file.path(PROJHOME, "Data", "data_processed", 
                                     "survey_orgs_all.rds"))

# Load cleaned, country-based survey data (*with* the Q4\* loop)
survey.clean.all <- readRDS(file.path(PROJHOME, "Data", "data_processed", 
                                      "survey_clean_all.rds"))

# Load cleaned, organization-based data (without the Q4 loop)
survey.orgs.clean <- readRDS(file.path(PROJHOME, "Data", "data_processed", 
                                       "survey_orgs_clean.rds"))

# Load cleaned, country-based data (only the Q4 loop)
survey.countries.clean <- readRDS(file.path(PROJHOME, "Data", "data_processed", 
                                            "survey_countries_clean.rds"))

# Load valid partial responses
survey.partials <- readRDS(file.path(PROJHOME, "Data", "data_processed", 
                                     "survey_partials.rds"))
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
  select(-c(description))

response.summary.total <- response.summary %>%
  summarise_each(funs(sum), -title, -name) %>%
  mutate(title = "**Total**")

response.summary.with.total <- bind_rows(response.summary,
                                         response.summary.total) %>%
  select(-name) %>%
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

Some databases were more responsive than others (though this is hardly
accurate; half of the responses aren't linked to specific databases):


```r
survey.dbs <- survey.orgs.clean %>%
  group_by(database) %>%
  summarise(num.responses = n()) %>% 
  ungroup()

response.summary.actual <- survey.dbs %>%
  left_join(response.summary, by=c("database"="name")) %>%
  mutate(pct.responded.from.invited = num.responses / num.invited,
         pct.responded.clean = percent(pct.responded.from.invited)) %>%
  mutate(database = ifelse(database == "unknown", "zzzunknown", database),
         title = ifelse(is.na(title), "Unknown", title)) %>%
  arrange(database) %>%
  select(title, num.responses, num.invited, pct.responded.clean)
```

```r
pandoc.table(response.summary.actual)
```


-----------------------------------------------------------------------------------------------------------
title                                                   num.responses   num.invited   pct.responded.clean  
------------------------------------------------------- --------------- ------------- ---------------------
Arab Institute of Human Rights NGO directory            4               397           1.01%                

Directory of Development Organizations                  59              7083          0.83%                

UN Integrated Civil Society Organizations System (iCSO) 321             6397          5.02%                

Global Anti-Human Trafficking (TIP) NGOs                30              970           3.09%                

Yearbook of International Organizations (YBIO)          80              2743          2.92%                

Unknown                                                 349             NA            NA%                  
-----------------------------------------------------------------------------------------------------------

## Figure out partials, incompletes, completes

Determine the best cutoff point for partially answered questions based on
the number of questions answered.

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

However, some respondents quit before answering any questions about the 
countries they work in. I count any respondent that answered more than six 
questions in the loop of country questions. I use six because of how the Q4
variables are generated and cleaned. If an organization answered Q4.1 (the
country name), the script converted it to COW and ISO codes, resulting in 3
valid Q4.1 questions. Additionally, the script converts text-based Q4
questions into characters and will sometimes yield NULL instead of NA, which
then gets counted in the number of questions (so it's possible for a
respondent to answer just the country name and have that count as 6
questions). More than six quesion.

So, I use a combination of factors to determine partiality. A respondent has
to answer at least 20 questions, and at least 6 have to come from the Q4
loop. This is a better, more robust cutoff than simply using a 20-question
minimum arbitrarily.

Thus, there are this many valid partial responses:



```r
nrow(survey.orgs.clean)
```

```
## [1] 843
```

```r
table(survey.orgs.clean$complete)
```

```
## 
## FALSE  TRUE 
##   307   536
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
  filter(!(ResponseID %in% unique(c(survey.partials$ResponseID,
                                    survey.clean.all$ResponseID)))) %>%
  select(ResponseID) %>% unique() %>% nrow() %>% unlist()

I.survey <- survey.clean.all %>%
  filter(Finished == 1) %>% select(ResponseID) %>% 
  unique() %>% nrow() %>% unlist()

P.survey <- length(unique(survey.partials$ResponseID))

break.off.rate <- BO / (I.survey + P.survey + BO)
```

- BO = number of surveys broken off (i.e. incomplete and 
  not partial): 102
- I = complete: 536
- P = partial: 307
- **Break-off rate:** 10.8% 

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

- I = complete: 536
- P = partial: 307
- R = refusal and break-off: 102 (break-off) and 
  2 (refusal)
- NC = non-contact: 15,772
- O = other: None
- **Participation rate**: 5.04%

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

- SCQ = screening completed and qualified: 945
- SCNQ = screening completed and not qualified (i.e. screened out): 478
- INV = survey invitations sent out: 17,590
- **Study-specific screening completion rate**: 8.09%

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

- SCQ = screening completed and qualified: 945
- SCNQ = screening completed and not qualified (i.e. screened out): 478
- **Study-specific eligibility rate**: 66.4%

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
  gather(email_type, email_date, starts_with("email")) %>%
  # Make Group 9's reminder be the final reminder
  mutate(email_type = ifelse(email_type == "email_reminder" & id_group == 9,
                             "email_final_reminder", email_type))


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

<!--html_preserve--><div id="htmlwidget-5736" style="width:672px;height:480px;" class="plotly html-widget"></div>
<script type="application/json" data-for="htmlwidget-5736">{"x":{"data":[{"x":[1461196800,1461283200,1461369600,1461888000,1461974400,1462233600,1462320000,1462924800,1465257600,1465344000,1465344000,1467158400],"y":[1293,3003,4223,6725,8093,16955,21178,33910,46642,50865,51500,52135],"text":["email_day: 2016-04-20 20:00:00<br>total: 1293","email_day: 2016-04-21 20:00:00<br>total: 3003","email_day: 2016-04-22 20:00:00<br>total: 4223","email_day: 2016-04-28 20:00:00<br>total: 6725","email_day: 2016-04-29 20:00:00<br>total: 8093","email_day: 2016-05-02 20:00:00<br>total: 16955","email_day: 2016-05-03 20:00:00<br>total: 21178","email_day: 2016-05-10 20:00:00<br>total: 33910","email_day: 2016-06-06 20:00:00<br>total: 46642","email_day: 2016-06-07 20:00:00<br>total: 50865","email_day: 2016-06-07 20:00:00<br>total: 51500","email_day: 2016-06-28 20:00:00<br>total: 52135"],"key":null,"type":"scatter","mode":"lines","name":"","line":{"width":1.88976377952756,"color":"rgba(127,127,127,1)","dash":"solid","shape":"hv"},"showlegend":false,"xaxis":"x","yaxis":"y","hoverinfo":"text"},{"x":[1461196800,1461283200,1461369600,1461888000,1461974400,1462233600,1465344000],"y":[1293,3003,4223,6725,8093,16955,51500],"text":["email_day: 2016-04-20 20:00:00<br>total: 1293<br>email_type: Invitation  <br>Groups 1-3","email_day: 2016-04-21 20:00:00<br>total: 3003<br>email_type: Invitation  <br>Groups 4-6","email_day: 2016-04-22 20:00:00<br>total: 4223<br>email_type: Invitation  <br>Groups 7-8","email_day: 2016-04-28 20:00:00<br>total: 6725<br>email_type: Invitation  <br>Groups 10-13","email_day: 2016-04-29 20:00:00<br>total: 8093<br>email_type: Invitation  <br>Groups 14-15","email_day: 2016-05-02 20:00:00<br>total: 16955<br>email_type: Invitation  <br>Groups 16-28","email_day: 2016-06-07 20:00:00<br>total: 51500<br>email_type: Invitation  <br>Group 9"],"key":null,"type":"scatter","mode":"markers","marker":{"autocolorscale":false,"color":"rgba(248,118,109,1)","opacity":1,"size":5.66929133858268,"symbol":"circle","line":{"width":1.88976377952756,"color":"rgba(248,118,109,1)"}},"name":"Invitation  ","legendgroup":"Invitation  ","showlegend":true,"xaxis":"x","yaxis":"y","hoverinfo":"text"},{"x":[1462320000,1462924800],"y":[21178,33910],"text":["email_day: 2016-05-03 20:00:00<br>total: 21178<br>email_type: Reminder  <br>Groups 1-8","email_day: 2016-05-10 20:00:00<br>total: 33910<br>email_type: Reminder  <br>Groups 10-28"],"key":null,"type":"scatter","mode":"markers","marker":{"autocolorscale":false,"color":"rgba(0,186,56,1)","opacity":1,"size":5.66929133858268,"symbol":"circle","line":{"width":1.88976377952756,"color":"rgba(0,186,56,1)"}},"name":"Reminder  ","legendgroup":"Reminder  ","showlegend":true,"xaxis":"x","yaxis":"y","hoverinfo":"text"},{"x":[1465257600,1465344000,1467158400],"y":[46642,50865,52135],"text":["email_day: 2016-06-06 20:00:00<br>total: 46642<br>email_type: Final reminder<br>Groups 10-28","email_day: 2016-06-07 20:00:00<br>total: 50865<br>email_type: Final reminder<br>Groups 1-8","email_day: 2016-06-28 20:00:00<br>total: 52135<br>email_type: Final reminder<br>Group 9"],"key":null,"type":"scatter","mode":"markers","marker":{"autocolorscale":false,"color":"rgba(97,156,255,1)","opacity":1,"size":5.66929133858268,"symbol":"circle","line":{"width":1.88976377952756,"color":"rgba(97,156,255,1)"}},"name":"Final reminder","legendgroup":"Final reminder","showlegend":true,"xaxis":"x","yaxis":"y","hoverinfo":"text"}],"layout":{"margin":{"b":27.8953922789539,"l":66.1519302615193,"t":27.1581569115816,"r":7.97011207970112},"plot_bgcolor":"rgba(255,255,255,1)","paper_bgcolor":"rgba(255,255,255,1)","font":{"color":"rgba(0,0,0,1)","family":"","size":15.9402241594022},"xaxis":{"type":"linear","autorange":false,"tickmode":"array","range":[1460898720,1467456480],"ticktext":["April 18","April 25","May  2","May  9","May 16","May 23","May 30","June  6","June 13","June 20","June 27"],"tickvals":[1460937600,1461542400,1462147200,1462752000,1463356800,1463961600,1464566400,1465171200,1465776000,1466380800,1466985600],"ticks":"outside","tickcolor":"rgba(179,179,179,1)","ticklen":3.98505603985056,"tickwidth":0.33208800332088,"showticklabels":true,"tickfont":{"color":"rgba(77,77,77,1)","family":"","size":12.7521793275218},"tickangle":-0,"showline":false,"linecolor":null,"linewidth":0,"showgrid":true,"domain":[0,1],"gridcolor":"rgba(217,217,217,1)","gridwidth":0.33208800332088,"zeroline":false,"anchor":"y","title":"","titlefont":{"color":"rgba(0,0,0,1)","family":"","size":15.9402241594022},"hoverformat":".2f"},"yaxis":{"type":"linear","autorange":false,"tickmode":"array","range":[-1249.1,54677.1],"ticktext":["0","10,000","20,000","30,000","40,000","50,000"],"tickvals":[0,10000,20000,30000,40000,50000],"ticks":"outside","tickcolor":"rgba(179,179,179,1)","ticklen":3.98505603985056,"tickwidth":0.33208800332088,"showticklabels":true,"tickfont":{"color":"rgba(77,77,77,1)","family":"","size":12.7521793275218},"tickangle":-0,"showline":false,"linecolor":null,"linewidth":0,"showgrid":true,"domain":[0,1],"gridcolor":"rgba(217,217,217,1)","gridwidth":0.33208800332088,"zeroline":false,"anchor":"x","title":"Approximate total number of emails","titlefont":{"color":"rgba(0,0,0,1)","family":"","size":15.9402241594022},"hoverformat":".2f"},"shapes":[{"type":"rect","fillcolor":"transparent","line":{"color":"rgba(179,179,179,1)","width":0.66417600664176,"linetype":"solid"},"yref":"paper","xref":"paper","x0":0,"x1":1,"y0":0,"y1":1}],"showlegend":true,"legend":{"bgcolor":"rgba(255,255,255,1)","bordercolor":"transparent","borderwidth":1.88976377952756,"font":{"color":"rgba(0,0,0,1)","family":"","size":12.7521793275218},"y":1},"hovermode":"closest"},"source":"A","config":{"modeBarButtonsToRemove":["sendDataToCloud"]},"base_url":"https://plot.ly"},"evals":[],"jsHooks":[]}</script><!--/html_preserve-->

## Timeline of survey responses


```r
survey.time.plot <- survey.orgs.clean %>%
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

<!--html_preserve--><div id="htmlwidget-1194" style="width:672px;height:480px;" class="plotly html-widget"></div>
<script type="application/json" data-for="htmlwidget-1194">{"x":{"data":[{"x":[1461172871,1461175205,1461178013,1461178218,1461179934,1461188367,1461191621,1461193969,1461198809,1461199308,1461208238,1461208973,1461210053,1461216330,1461220382,1461222746,1461232926,1461235755,1461238929,1461240578,1461241221,1461249469,1461251376,1461252980,1461253467,1461256412,1461257446,1461259492,1461259825,1461261365,1461263247,1461263702,1461266777,1461267859,1461272024,1461277983,1461285841,1461288655,1461292369,1461294450,1461296570,1461297974,1461299294,1461299539,1461300020,1461301925,1461302433,1461305921,1461306744,1461308434,1461309322,1461313975,1461314995,1461316204,1461319559,1461320094,1461323255,1461325215,1461326441,1461329400,1461329790,1461335646,1461337055,1461337092,1461337270,1461337925,1461340114,1461344149,1461356158,1461362601,1461364525,1461366567,1461370255,1461376829,1461379596,1461403519,1461403583,1461414458,1461420578,1461420669,1461423681,1461424860,1461429365,1461437253,1461487964,1461532853,1461536263,1461553728,1461559483,1461559577,1461560532,1461566049,1461566552,1461585671,1461586581,1461587349,1461589707,1461594094,1461597189,1461602309,1461603614,1461604125,1461604500,1461604834,1461641026,1461642570,1461646792,1461651023,1461652953,1461657730,1461659552,1461662133,1461665652,1461667994,1461671605,1461679331,1461679386,1461682953,1461685982,1461705046,1461724505,1461734541,1461746925,1461749295,1461756690,1461761978,1461781438,1461797893,1461798488,1461831800,1461837659,1461840757,1461841224,1461843604,1461848617,1461849280,1461849375,1461850206,1461850734,1461851198,1461851524,1461851532,1461852730,1461852948,1461854870,1461856691,1461857189,1461859929,1461860786,1461865098,1461866342,1461869824,1461877983,1461881438,1461883030,1461885288,1461886318,1461889850,1461892140,1461894372,1461901329,1461906610,1461912420,1461918711,1461919553,1461924939,1461929598,1461932909,1461933163,1461935224,1461935437,1461936032,1461937829,1461938423,1461939772,1461945035,1461965136,1461969284,1461987537,1461994578,1461996857,1461997522,1461998286,1462003949,1462004313,1462006093,1462017314,1462017429,1462018299,1462054141,1462087016,1462089015,1462094253,1462095244,1462105848,1462112661,1462149451,1462160340,1462161318,1462166046,1462174836,1462183302,1462185559,1462186933,1462187000,1462187077,1462187092,1462187101,1462187370,1462187680,1462187868,1462189004,1462189331,1462189479,1462189781,1462189806,1462190302,1462190370,1462190640,1462190861,1462191238,1462191503,1462191702,1462191818,1462192090,1462192356,1462192421,1462192542,1462192542,1462192564,1462192769,1462192777,1462193008,1462193047,1462193206,1462193753,1462193876,1462194291,1462194292,1462194436,1462194445,1462194754,1462194836,1462195237,1462195420,1462195776,1462195825,1462195829,1462196354,1462196511,1462197483,1462197984,1462199014,1462199064,1462199389,1462199457,1462199634,1462199731,1462199746,1462199797,1462200040,1462200178,1462201239,1462201716,1462201868,1462202203,1462202402,1462203158,1462205310,1462205493,1462205919,1462205956,1462206186,1462206374,1462206916,1462207112,1462207934,1462208100,1462212142,1462214042,1462214059,1462216349,1462218086,1462222440,1462224019,1462224880,1462225139,1462228153,1462232027,1462232525,1462234505,1462234517,1462238513,1462239764,1462242891,1462244072,1462245292,1462248226,1462249277,1462249493,1462250969,1462251267,1462252448,1462253452,1462255556,1462257460,1462258808,1462258901,1462259084,1462259502,1462259773,1462261448,1462262087,1462262139,1462265300,1462266009,1462267305,1462267388,1462268152,1462269286,1462270030,1462270337,1462270605,1462270770,1462271175,1462271354,1462271536,1462271863,1462271959,1462272050,1462272810,1462273395,1462275552,1462275810,1462276153,1462276446,1462277854,1462278232,1462280208,1462280857,1462285365,1462287776,1462289645,1462289897,1462290008,1462290665,1462290865,1462291184,1462291299,1462291519,1462291847,1462291976,1462292417,1462292544,1462293577,1462294608,1462296206,1462296248,1462297322,1462299519,1462301526,1462304126,1462306004,1462309545,1462311571,1462320300,1462322313,1462322585,1462324224,1462324689,1462326620,1462328748,1462329636,1462332386,1462334691,1462335556,1462337178,1462339644,1462342492,1462342964,1462346319,1462347187,1462352677,1462353203,1462353843,1462358716,1462359772,1462360028,1462360576,1462361236,1462363467,1462363752,1462364851,1462368992,1462371890,1462372219,1462378099,1462378281,1462382079,1462384728,1462387322,1462399606,1462401821,1462410599,1462426318,1462433000,1462434744,1462436425,1462440282,1462447626,1462451394,1462451875,1462454654,1462455824,1462457718,1462458480,1462458621,1462462280,1462476076,1462478558,1462479040,1462480532,1462501959,1462507235,1462518083,1462524245,1462524983,1462527906,1462528064,1462532840,1462563850,1462573492,1462623357,1462627518,1462636046,1462659219,1462672167,1462704573,1462709259,1462742474,1462764494,1462768309,1462780559,1462784134,1462788870,1462789253,1462813022,1462819446,1462827787,1462846821,1462848818,1462855470,1462857011,1462857441,1462860821,1462870299,1462870698,1462873399,1462873862,1462874191,1462874366,1462875176,1462875631,1462876109,1462876436,1462877268,1462879201,1462879207,1462879245,1462879494,1462880571,1462880868,1462881255,1462881284,1462881736,1462881739,1462881885,1462882166,1462882460,1462882736,1462883241,1462883646,1462883903,1462883968,1462884809,1462885506,1462885512,1462885553,1462885852,1462885876,1462885954,1462886064,1462887051,1462887284,1462887775,1462888643,1462889019,1462893083,1462893110,1462893685,1462894319,1462894704,1462894869,1462896034,1462896285,1462897066,1462897444,1462897783,1462898098,1462898448,1462899163,1462899470,1462901306,1462901826,1462902323,1462904543,1462905196,1462905666,1462906217,1462907181,1462907438,1462910615,1462915755,1462917076,1462917272,1462917375,1462919382,1462921682,1462923425,1462928684,1462932169,1462932673,1462933247,1462934774,1462935183,1462936758,1462938948,1462939296,1462940055,1462940480,1462940547,1462940957,1462941614,1462942162,1462942180,1462943634,1462943897,1462944030,1462945035,1462947284,1462948216,1462949290,1462950096,1462951353,1462951405,1462953620,1462953886,1462954070,1462954116,1462954945,1462957800,1462958633,1462960778,1462960780,1462962211,1462962298,1462964780,1462965404,1462965964,1462967697,1462967819,1462968464,1462969197,1462971455,1462971485,1462972002,1462973323,1462975667,1462979602,1462981708,1462983063,1462984912,1462986151,1462989722,1462992881,1462996533,1463004659,1463006258,1463020211,1463025183,1463025883,1463027015,1463036492,1463036625,1463037955,1463040956,1463052112,1463057064,1463057252,1463058089,1463060739,1463062632,1463063099,1463064000,1463068090,1463082896,1463088922,1463089208,1463089804,1463109184,1463110292,1463113405,1463120075,1463121737,1463123177,1463123212,1463128443,1463128965,1463130908,1463130942,1463136335,1463138693,1463147273,1463148876,1463151417,1463153312,1463153986,1463224906,1463287280,1463297327,1463297704,1463300250,1463306845,1463314559,1463330241,1463359043,1463372267,1463373528,1463375800,1463384611,1463399021,1463399950,1463407396,1463452053,1463465392,1463468270,1463468771,1463471066,1463475144,1463475311,1463475334,1463480195,1463487531,1463489100,1463499915,1463513442,1463533054,1463542712,1463549827,1463558017,1463564666,1463573721,1463583833,1463599008,1463611621,1463631857,1463674077,1463688301,1463750047,1463773002,1464003232,1464021607,1464133638,1464239046,1464430228,1464648100,1464753080,1464890805,1465186169,1465226948,1465227071,1465227961,1465228627,1465230055,1465230067,1465230488,1465230875,1465230887,1465231150,1465232657,1465233911,1465233970,1465233993,1465235635,1465236134,1465238142,1465238411,1465238499,1465240190,1465241740,1465244792,1465246849,1465247321,1465247401,1465248196,1465250987,1465253084,1465253465,1465254542,1465255497,1465256239,1465261980,1465268764,1465269517,1465269742,1465270586,1465270624,1465271144,1465272333,1465272420,1465274543,1465274860,1465275734,1465276336,1465276540,1465278025,1465278443,1465278569,1465278940,1465279627,1465279774,1465280339,1465280840,1465281898,1465282582,1465282789,1465284405,1465284675,1465285269,1465285457,1465286202,1465286818,1465291095,1465294293,1465294999,1465300941,1465301729,1465303710,1465304394,1465305147,1465305827,1465308962,1465310007,1465321276,1465326792,1465332195,1465335829,1465337737,1465338551,1465339924,1465341696,1465344172,1465351918,1465355666,1465359115,1465359234,1465363714,1465367306,1465370816,1465375441,1465377781,1465381370,1465381678,1465384850,1465388290,1465392701,1465393703,1465395611,1465397836,1465404367,1465404978,1465408539,1465420769,1465444629,1465448021,1465449529,1465457474,1465467094,1465467587,1465472203,1465485659,1465486198,1465495512,1465497925,1465504982,1465506748,1465517651,1465526809,1465553691,1465553949,1465555016,1465560139,1465562234,1465563200,1465577109,1465579763,1465591944,1465593820,1465622106,1465648297,1465654313,1465658843,1465713957,1465730322,1465806746,1465808465,1465910089,1465912205,1465966112,1465980745,1465983324,1465986936,1465988925,1466000156,1466082588,1466120510,1466167639,1466213412,1466219588,1466318864,1466398212,1466445010,1466449732,1466516527,1466546160,1467163964,1467166334,1467186490,1467189650,1467197229,1467222135,1467388733,1467693554],"y":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,441,442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461,462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477,478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500,501,502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,539,540,541,542,543,544,545,546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562,563,564,565,566,567,568,569,570,571,572,573,574,575,576,577,578,579,580,581,582,583,584,585,586,587,588,589,590,591,592,593,594,595,596,597,598,599,600,601,602,603,604,605,606,607,608,609,610,611,612,613,614,615,616,617,618,619,620,621,622,623,624,625,626,627,628,629,630,631,632,633,634,635,636,637,638,639,640,641,642,643,644,645,646,647,648,649,650,651,652,653,654,655,656,657,658,659,660,661,662,663,664,665,666,667,668,669,670,671,672,673,674,675,676,677,678,679,680,681,682,683,684,685,686,687,688,689,690,691,692,693,694,695,696,697,698,699,700,701,702,703,704,705,706,707,708,709,710,711,712,713,714,715,716,717,718,719,720,721,722,723,724,725,726,727,728,729,730,731,732,733,734,735,736,737,738,739,740,741,742,743,744,745,746,747,748,749,750,751,752,753,754,755,756,757,758,759,760,761,762,763,764,765,766,767,768,769,770,771,772,773,774,775,776,777,778,779,780,781,782,783,784,785,786,787,788,789,790,791,792,793,794,795,796,797,798,799,800,801,802,803,804,805,806,807,808,809,810,811,812,813,814,815,816,817,818,819,820,821,822,823,824,825,826,827,828,829,830,831,832,833,834,835,836,837,838,839,840,841,842,843],"text":["EndDate: 2016-04-20 13:21:11<br>num.completed.cum: 1","EndDate: 2016-04-20 14:00:05<br>num.completed.cum: 2","EndDate: 2016-04-20 14:46:53<br>num.completed.cum: 3","EndDate: 2016-04-20 14:50:18<br>num.completed.cum: 4","EndDate: 2016-04-20 15:18:54<br>num.completed.cum: 5","EndDate: 2016-04-20 17:39:27<br>num.completed.cum: 6","EndDate: 2016-04-20 18:33:41<br>num.completed.cum: 7","EndDate: 2016-04-20 19:12:49<br>num.completed.cum: 8","EndDate: 2016-04-20 20:33:29<br>num.completed.cum: 9","EndDate: 2016-04-20 20:41:48<br>num.completed.cum: 10","EndDate: 2016-04-20 23:10:38<br>num.completed.cum: 11","EndDate: 2016-04-20 23:22:53<br>num.completed.cum: 12","EndDate: 2016-04-20 23:40:53<br>num.completed.cum: 13","EndDate: 2016-04-21 01:25:30<br>num.completed.cum: 14","EndDate: 2016-04-21 02:33:02<br>num.completed.cum: 15","EndDate: 2016-04-21 03:12:26<br>num.completed.cum: 16","EndDate: 2016-04-21 06:02:06<br>num.completed.cum: 17","EndDate: 2016-04-21 06:49:15<br>num.completed.cum: 18","EndDate: 2016-04-21 07:42:09<br>num.completed.cum: 19","EndDate: 2016-04-21 08:09:38<br>num.completed.cum: 20","EndDate: 2016-04-21 08:20:21<br>num.completed.cum: 21","EndDate: 2016-04-21 10:37:49<br>num.completed.cum: 22","EndDate: 2016-04-21 11:09:36<br>num.completed.cum: 23","EndDate: 2016-04-21 11:36:20<br>num.completed.cum: 24","EndDate: 2016-04-21 11:44:27<br>num.completed.cum: 25","EndDate: 2016-04-21 12:33:32<br>num.completed.cum: 26","EndDate: 2016-04-21 12:50:46<br>num.completed.cum: 27","EndDate: 2016-04-21 13:24:52<br>num.completed.cum: 28","EndDate: 2016-04-21 13:30:25<br>num.completed.cum: 29","EndDate: 2016-04-21 13:56:05<br>num.completed.cum: 30","EndDate: 2016-04-21 14:27:27<br>num.completed.cum: 31","EndDate: 2016-04-21 14:35:02<br>num.completed.cum: 32","EndDate: 2016-04-21 15:26:17<br>num.completed.cum: 33","EndDate: 2016-04-21 15:44:19<br>num.completed.cum: 34","EndDate: 2016-04-21 16:53:44<br>num.completed.cum: 35","EndDate: 2016-04-21 18:33:03<br>num.completed.cum: 36","EndDate: 2016-04-21 20:44:01<br>num.completed.cum: 37","EndDate: 2016-04-21 21:30:55<br>num.completed.cum: 38","EndDate: 2016-04-21 22:32:49<br>num.completed.cum: 39","EndDate: 2016-04-21 23:07:30<br>num.completed.cum: 40","EndDate: 2016-04-21 23:42:50<br>num.completed.cum: 41","EndDate: 2016-04-22 00:06:14<br>num.completed.cum: 42","EndDate: 2016-04-22 00:28:14<br>num.completed.cum: 43","EndDate: 2016-04-22 00:32:19<br>num.completed.cum: 44","EndDate: 2016-04-22 00:40:20<br>num.completed.cum: 45","EndDate: 2016-04-22 01:12:05<br>num.completed.cum: 46","EndDate: 2016-04-22 01:20:33<br>num.completed.cum: 47","EndDate: 2016-04-22 02:18:41<br>num.completed.cum: 48","EndDate: 2016-04-22 02:32:24<br>num.completed.cum: 49","EndDate: 2016-04-22 03:00:34<br>num.completed.cum: 50","EndDate: 2016-04-22 03:15:22<br>num.completed.cum: 51","EndDate: 2016-04-22 04:32:55<br>num.completed.cum: 52","EndDate: 2016-04-22 04:49:55<br>num.completed.cum: 53","EndDate: 2016-04-22 05:10:04<br>num.completed.cum: 54","EndDate: 2016-04-22 06:05:59<br>num.completed.cum: 55","EndDate: 2016-04-22 06:14:54<br>num.completed.cum: 56","EndDate: 2016-04-22 07:07:35<br>num.completed.cum: 57","EndDate: 2016-04-22 07:40:15<br>num.completed.cum: 58","EndDate: 2016-04-22 08:00:41<br>num.completed.cum: 59","EndDate: 2016-04-22 08:50:00<br>num.completed.cum: 60","EndDate: 2016-04-22 08:56:30<br>num.completed.cum: 61","EndDate: 2016-04-22 10:34:06<br>num.completed.cum: 62","EndDate: 2016-04-22 10:57:35<br>num.completed.cum: 63","EndDate: 2016-04-22 10:58:12<br>num.completed.cum: 64","EndDate: 2016-04-22 11:01:10<br>num.completed.cum: 65","EndDate: 2016-04-22 11:12:05<br>num.completed.cum: 66","EndDate: 2016-04-22 11:48:34<br>num.completed.cum: 67","EndDate: 2016-04-22 12:55:49<br>num.completed.cum: 68","EndDate: 2016-04-22 16:15:58<br>num.completed.cum: 69","EndDate: 2016-04-22 18:03:21<br>num.completed.cum: 70","EndDate: 2016-04-22 18:35:25<br>num.completed.cum: 71","EndDate: 2016-04-22 19:09:27<br>num.completed.cum: 72","EndDate: 2016-04-22 20:10:55<br>num.completed.cum: 73","EndDate: 2016-04-22 22:00:29<br>num.completed.cum: 74","EndDate: 2016-04-22 22:46:36<br>num.completed.cum: 75","EndDate: 2016-04-23 05:25:19<br>num.completed.cum: 76","EndDate: 2016-04-23 05:26:23<br>num.completed.cum: 77","EndDate: 2016-04-23 08:27:38<br>num.completed.cum: 78","EndDate: 2016-04-23 10:09:38<br>num.completed.cum: 79","EndDate: 2016-04-23 10:11:09<br>num.completed.cum: 80","EndDate: 2016-04-23 11:01:21<br>num.completed.cum: 81","EndDate: 2016-04-23 11:21:00<br>num.completed.cum: 82","EndDate: 2016-04-23 12:36:05<br>num.completed.cum: 83","EndDate: 2016-04-23 14:47:33<br>num.completed.cum: 84","EndDate: 2016-04-24 04:52:44<br>num.completed.cum: 85","EndDate: 2016-04-24 17:20:53<br>num.completed.cum: 86","EndDate: 2016-04-24 18:17:43<br>num.completed.cum: 87","EndDate: 2016-04-24 23:08:48<br>num.completed.cum: 88","EndDate: 2016-04-25 00:44:43<br>num.completed.cum: 89","EndDate: 2016-04-25 00:46:17<br>num.completed.cum: 90","EndDate: 2016-04-25 01:02:12<br>num.completed.cum: 91","EndDate: 2016-04-25 02:34:09<br>num.completed.cum: 92","EndDate: 2016-04-25 02:42:32<br>num.completed.cum: 93","EndDate: 2016-04-25 08:01:11<br>num.completed.cum: 94","EndDate: 2016-04-25 08:16:21<br>num.completed.cum: 95","EndDate: 2016-04-25 08:29:09<br>num.completed.cum: 96","EndDate: 2016-04-25 09:08:27<br>num.completed.cum: 97","EndDate: 2016-04-25 10:21:34<br>num.completed.cum: 98","EndDate: 2016-04-25 11:13:09<br>num.completed.cum: 99","EndDate: 2016-04-25 12:38:29<br>num.completed.cum: 100","EndDate: 2016-04-25 13:00:14<br>num.completed.cum: 101","EndDate: 2016-04-25 13:08:45<br>num.completed.cum: 102","EndDate: 2016-04-25 13:15:00<br>num.completed.cum: 103","EndDate: 2016-04-25 13:20:34<br>num.completed.cum: 104","EndDate: 2016-04-25 23:23:46<br>num.completed.cum: 105","EndDate: 2016-04-25 23:49:30<br>num.completed.cum: 106","EndDate: 2016-04-26 00:59:52<br>num.completed.cum: 107","EndDate: 2016-04-26 02:10:23<br>num.completed.cum: 108","EndDate: 2016-04-26 02:42:33<br>num.completed.cum: 109","EndDate: 2016-04-26 04:02:10<br>num.completed.cum: 110","EndDate: 2016-04-26 04:32:32<br>num.completed.cum: 111","EndDate: 2016-04-26 05:15:33<br>num.completed.cum: 112","EndDate: 2016-04-26 06:14:12<br>num.completed.cum: 113","EndDate: 2016-04-26 06:53:14<br>num.completed.cum: 114","EndDate: 2016-04-26 07:53:25<br>num.completed.cum: 115","EndDate: 2016-04-26 10:02:11<br>num.completed.cum: 116","EndDate: 2016-04-26 10:03:06<br>num.completed.cum: 117","EndDate: 2016-04-26 11:02:33<br>num.completed.cum: 118","EndDate: 2016-04-26 11:53:02<br>num.completed.cum: 119","EndDate: 2016-04-26 17:10:46<br>num.completed.cum: 120","EndDate: 2016-04-26 22:35:05<br>num.completed.cum: 121","EndDate: 2016-04-27 01:22:21<br>num.completed.cum: 122","EndDate: 2016-04-27 04:48:45<br>num.completed.cum: 123","EndDate: 2016-04-27 05:28:15<br>num.completed.cum: 124","EndDate: 2016-04-27 07:31:30<br>num.completed.cum: 125","EndDate: 2016-04-27 08:59:38<br>num.completed.cum: 126","EndDate: 2016-04-27 14:23:58<br>num.completed.cum: 127","EndDate: 2016-04-27 18:58:13<br>num.completed.cum: 128","EndDate: 2016-04-27 19:08:08<br>num.completed.cum: 129","EndDate: 2016-04-28 04:23:20<br>num.completed.cum: 130","EndDate: 2016-04-28 06:00:59<br>num.completed.cum: 131","EndDate: 2016-04-28 06:52:37<br>num.completed.cum: 132","EndDate: 2016-04-28 07:00:24<br>num.completed.cum: 133","EndDate: 2016-04-28 07:40:04<br>num.completed.cum: 134","EndDate: 2016-04-28 09:03:37<br>num.completed.cum: 135","EndDate: 2016-04-28 09:14:40<br>num.completed.cum: 136","EndDate: 2016-04-28 09:16:15<br>num.completed.cum: 137","EndDate: 2016-04-28 09:30:06<br>num.completed.cum: 138","EndDate: 2016-04-28 09:38:54<br>num.completed.cum: 139","EndDate: 2016-04-28 09:46:38<br>num.completed.cum: 140","EndDate: 2016-04-28 09:52:04<br>num.completed.cum: 141","EndDate: 2016-04-28 09:52:12<br>num.completed.cum: 142","EndDate: 2016-04-28 10:12:10<br>num.completed.cum: 143","EndDate: 2016-04-28 10:15:48<br>num.completed.cum: 144","EndDate: 2016-04-28 10:47:50<br>num.completed.cum: 145","EndDate: 2016-04-28 11:18:11<br>num.completed.cum: 146","EndDate: 2016-04-28 11:26:29<br>num.completed.cum: 147","EndDate: 2016-04-28 12:12:09<br>num.completed.cum: 148","EndDate: 2016-04-28 12:26:26<br>num.completed.cum: 149","EndDate: 2016-04-28 13:38:18<br>num.completed.cum: 150","EndDate: 2016-04-28 13:59:02<br>num.completed.cum: 151","EndDate: 2016-04-28 14:57:04<br>num.completed.cum: 152","EndDate: 2016-04-28 17:13:03<br>num.completed.cum: 153","EndDate: 2016-04-28 18:10:38<br>num.completed.cum: 154","EndDate: 2016-04-28 18:37:10<br>num.completed.cum: 155","EndDate: 2016-04-28 19:14:48<br>num.completed.cum: 156","EndDate: 2016-04-28 19:31:58<br>num.completed.cum: 157","EndDate: 2016-04-28 20:30:50<br>num.completed.cum: 158","EndDate: 2016-04-28 21:09:00<br>num.completed.cum: 159","EndDate: 2016-04-28 21:46:12<br>num.completed.cum: 160","EndDate: 2016-04-28 23:42:09<br>num.completed.cum: 161","EndDate: 2016-04-29 01:10:10<br>num.completed.cum: 162","EndDate: 2016-04-29 02:47:00<br>num.completed.cum: 163","EndDate: 2016-04-29 04:31:51<br>num.completed.cum: 164","EndDate: 2016-04-29 04:45:53<br>num.completed.cum: 165","EndDate: 2016-04-29 06:15:39<br>num.completed.cum: 166","EndDate: 2016-04-29 07:33:18<br>num.completed.cum: 167","EndDate: 2016-04-29 08:28:29<br>num.completed.cum: 168","EndDate: 2016-04-29 08:32:43<br>num.completed.cum: 169","EndDate: 2016-04-29 09:07:04<br>num.completed.cum: 170","EndDate: 2016-04-29 09:10:37<br>num.completed.cum: 171","EndDate: 2016-04-29 09:20:32<br>num.completed.cum: 172","EndDate: 2016-04-29 09:50:29<br>num.completed.cum: 173","EndDate: 2016-04-29 10:00:23<br>num.completed.cum: 174","EndDate: 2016-04-29 10:22:52<br>num.completed.cum: 175","EndDate: 2016-04-29 11:50:35<br>num.completed.cum: 176","EndDate: 2016-04-29 17:25:36<br>num.completed.cum: 177","EndDate: 2016-04-29 18:34:44<br>num.completed.cum: 178","EndDate: 2016-04-29 23:38:57<br>num.completed.cum: 179","EndDate: 2016-04-30 01:36:18<br>num.completed.cum: 180","EndDate: 2016-04-30 02:14:17<br>num.completed.cum: 181","EndDate: 2016-04-30 02:25:22<br>num.completed.cum: 182","EndDate: 2016-04-30 02:38:06<br>num.completed.cum: 183","EndDate: 2016-04-30 04:12:29<br>num.completed.cum: 184","EndDate: 2016-04-30 04:18:33<br>num.completed.cum: 185","EndDate: 2016-04-30 04:48:13<br>num.completed.cum: 186","EndDate: 2016-04-30 07:55:14<br>num.completed.cum: 187","EndDate: 2016-04-30 07:57:09<br>num.completed.cum: 188","EndDate: 2016-04-30 08:11:39<br>num.completed.cum: 189","EndDate: 2016-04-30 18:09:01<br>num.completed.cum: 190","EndDate: 2016-05-01 03:16:56<br>num.completed.cum: 191","EndDate: 2016-05-01 03:50:15<br>num.completed.cum: 192","EndDate: 2016-05-01 05:17:33<br>num.completed.cum: 193","EndDate: 2016-05-01 05:34:04<br>num.completed.cum: 194","EndDate: 2016-05-01 08:30:48<br>num.completed.cum: 195","EndDate: 2016-05-01 10:24:21<br>num.completed.cum: 196","EndDate: 2016-05-01 20:37:31<br>num.completed.cum: 197","EndDate: 2016-05-01 23:39:00<br>num.completed.cum: 198","EndDate: 2016-05-01 23:55:18<br>num.completed.cum: 199","EndDate: 2016-05-02 01:14:06<br>num.completed.cum: 200","EndDate: 2016-05-02 03:40:36<br>num.completed.cum: 201","EndDate: 2016-05-02 06:01:42<br>num.completed.cum: 202","EndDate: 2016-05-02 06:39:19<br>num.completed.cum: 203","EndDate: 2016-05-02 07:02:13<br>num.completed.cum: 204","EndDate: 2016-05-02 07:03:20<br>num.completed.cum: 205","EndDate: 2016-05-02 07:04:37<br>num.completed.cum: 206","EndDate: 2016-05-02 07:04:52<br>num.completed.cum: 207","EndDate: 2016-05-02 07:05:01<br>num.completed.cum: 208","EndDate: 2016-05-02 07:09:30<br>num.completed.cum: 209","EndDate: 2016-05-02 07:14:40<br>num.completed.cum: 210","EndDate: 2016-05-02 07:17:48<br>num.completed.cum: 211","EndDate: 2016-05-02 07:36:44<br>num.completed.cum: 212","EndDate: 2016-05-02 07:42:11<br>num.completed.cum: 213","EndDate: 2016-05-02 07:44:39<br>num.completed.cum: 214","EndDate: 2016-05-02 07:49:41<br>num.completed.cum: 215","EndDate: 2016-05-02 07:50:06<br>num.completed.cum: 216","EndDate: 2016-05-02 07:58:22<br>num.completed.cum: 217","EndDate: 2016-05-02 07:59:30<br>num.completed.cum: 218","EndDate: 2016-05-02 08:04:00<br>num.completed.cum: 219","EndDate: 2016-05-02 08:07:41<br>num.completed.cum: 220","EndDate: 2016-05-02 08:13:58<br>num.completed.cum: 221","EndDate: 2016-05-02 08:18:23<br>num.completed.cum: 222","EndDate: 2016-05-02 08:21:42<br>num.completed.cum: 223","EndDate: 2016-05-02 08:23:38<br>num.completed.cum: 224","EndDate: 2016-05-02 08:28:10<br>num.completed.cum: 225","EndDate: 2016-05-02 08:32:36<br>num.completed.cum: 226","EndDate: 2016-05-02 08:33:41<br>num.completed.cum: 227","EndDate: 2016-05-02 08:35:42<br>num.completed.cum: 228","EndDate: 2016-05-02 08:35:42<br>num.completed.cum: 229","EndDate: 2016-05-02 08:36:04<br>num.completed.cum: 230","EndDate: 2016-05-02 08:39:29<br>num.completed.cum: 231","EndDate: 2016-05-02 08:39:37<br>num.completed.cum: 232","EndDate: 2016-05-02 08:43:28<br>num.completed.cum: 233","EndDate: 2016-05-02 08:44:07<br>num.completed.cum: 234","EndDate: 2016-05-02 08:46:46<br>num.completed.cum: 235","EndDate: 2016-05-02 08:55:53<br>num.completed.cum: 236","EndDate: 2016-05-02 08:57:56<br>num.completed.cum: 237","EndDate: 2016-05-02 09:04:51<br>num.completed.cum: 238","EndDate: 2016-05-02 09:04:52<br>num.completed.cum: 239","EndDate: 2016-05-02 09:07:16<br>num.completed.cum: 240","EndDate: 2016-05-02 09:07:25<br>num.completed.cum: 241","EndDate: 2016-05-02 09:12:34<br>num.completed.cum: 242","EndDate: 2016-05-02 09:13:56<br>num.completed.cum: 243","EndDate: 2016-05-02 09:20:37<br>num.completed.cum: 244","EndDate: 2016-05-02 09:23:40<br>num.completed.cum: 245","EndDate: 2016-05-02 09:29:36<br>num.completed.cum: 246","EndDate: 2016-05-02 09:30:25<br>num.completed.cum: 247","EndDate: 2016-05-02 09:30:29<br>num.completed.cum: 248","EndDate: 2016-05-02 09:39:14<br>num.completed.cum: 249","EndDate: 2016-05-02 09:41:51<br>num.completed.cum: 250","EndDate: 2016-05-02 09:58:03<br>num.completed.cum: 251","EndDate: 2016-05-02 10:06:24<br>num.completed.cum: 252","EndDate: 2016-05-02 10:23:34<br>num.completed.cum: 253","EndDate: 2016-05-02 10:24:24<br>num.completed.cum: 254","EndDate: 2016-05-02 10:29:49<br>num.completed.cum: 255","EndDate: 2016-05-02 10:30:57<br>num.completed.cum: 256","EndDate: 2016-05-02 10:33:54<br>num.completed.cum: 257","EndDate: 2016-05-02 10:35:31<br>num.completed.cum: 258","EndDate: 2016-05-02 10:35:46<br>num.completed.cum: 259","EndDate: 2016-05-02 10:36:37<br>num.completed.cum: 260","EndDate: 2016-05-02 10:40:40<br>num.completed.cum: 261","EndDate: 2016-05-02 10:42:58<br>num.completed.cum: 262","EndDate: 2016-05-02 11:00:39<br>num.completed.cum: 263","EndDate: 2016-05-02 11:08:36<br>num.completed.cum: 264","EndDate: 2016-05-02 11:11:08<br>num.completed.cum: 265","EndDate: 2016-05-02 11:16:43<br>num.completed.cum: 266","EndDate: 2016-05-02 11:20:02<br>num.completed.cum: 267","EndDate: 2016-05-02 11:32:38<br>num.completed.cum: 268","EndDate: 2016-05-02 12:08:30<br>num.completed.cum: 269","EndDate: 2016-05-02 12:11:33<br>num.completed.cum: 270","EndDate: 2016-05-02 12:18:39<br>num.completed.cum: 271","EndDate: 2016-05-02 12:19:16<br>num.completed.cum: 272","EndDate: 2016-05-02 12:23:06<br>num.completed.cum: 273","EndDate: 2016-05-02 12:26:14<br>num.completed.cum: 274","EndDate: 2016-05-02 12:35:16<br>num.completed.cum: 275","EndDate: 2016-05-02 12:38:32<br>num.completed.cum: 276","EndDate: 2016-05-02 12:52:14<br>num.completed.cum: 277","EndDate: 2016-05-02 12:55:00<br>num.completed.cum: 278","EndDate: 2016-05-02 14:02:22<br>num.completed.cum: 279","EndDate: 2016-05-02 14:34:02<br>num.completed.cum: 280","EndDate: 2016-05-02 14:34:19<br>num.completed.cum: 281","EndDate: 2016-05-02 15:12:29<br>num.completed.cum: 282","EndDate: 2016-05-02 15:41:26<br>num.completed.cum: 283","EndDate: 2016-05-02 16:54:00<br>num.completed.cum: 284","EndDate: 2016-05-02 17:20:19<br>num.completed.cum: 285","EndDate: 2016-05-02 17:34:40<br>num.completed.cum: 286","EndDate: 2016-05-02 17:38:59<br>num.completed.cum: 287","EndDate: 2016-05-02 18:29:13<br>num.completed.cum: 288","EndDate: 2016-05-02 19:33:47<br>num.completed.cum: 289","EndDate: 2016-05-02 19:42:05<br>num.completed.cum: 290","EndDate: 2016-05-02 20:15:05<br>num.completed.cum: 291","EndDate: 2016-05-02 20:15:17<br>num.completed.cum: 292","EndDate: 2016-05-02 21:21:53<br>num.completed.cum: 293","EndDate: 2016-05-02 21:42:44<br>num.completed.cum: 294","EndDate: 2016-05-02 22:34:51<br>num.completed.cum: 295","EndDate: 2016-05-02 22:54:32<br>num.completed.cum: 296","EndDate: 2016-05-02 23:14:52<br>num.completed.cum: 297","EndDate: 2016-05-03 00:03:46<br>num.completed.cum: 298","EndDate: 2016-05-03 00:21:17<br>num.completed.cum: 299","EndDate: 2016-05-03 00:24:53<br>num.completed.cum: 300","EndDate: 2016-05-03 00:49:29<br>num.completed.cum: 301","EndDate: 2016-05-03 00:54:27<br>num.completed.cum: 302","EndDate: 2016-05-03 01:14:08<br>num.completed.cum: 303","EndDate: 2016-05-03 01:30:52<br>num.completed.cum: 304","EndDate: 2016-05-03 02:05:56<br>num.completed.cum: 305","EndDate: 2016-05-03 02:37:40<br>num.completed.cum: 306","EndDate: 2016-05-03 03:00:08<br>num.completed.cum: 307","EndDate: 2016-05-03 03:01:41<br>num.completed.cum: 308","EndDate: 2016-05-03 03:04:44<br>num.completed.cum: 309","EndDate: 2016-05-03 03:11:42<br>num.completed.cum: 310","EndDate: 2016-05-03 03:16:13<br>num.completed.cum: 311","EndDate: 2016-05-03 03:44:08<br>num.completed.cum: 312","EndDate: 2016-05-03 03:54:47<br>num.completed.cum: 313","EndDate: 2016-05-03 03:55:39<br>num.completed.cum: 314","EndDate: 2016-05-03 04:48:20<br>num.completed.cum: 315","EndDate: 2016-05-03 05:00:09<br>num.completed.cum: 316","EndDate: 2016-05-03 05:21:45<br>num.completed.cum: 317","EndDate: 2016-05-03 05:23:08<br>num.completed.cum: 318","EndDate: 2016-05-03 05:35:52<br>num.completed.cum: 319","EndDate: 2016-05-03 05:54:46<br>num.completed.cum: 320","EndDate: 2016-05-03 06:07:10<br>num.completed.cum: 321","EndDate: 2016-05-03 06:12:17<br>num.completed.cum: 322","EndDate: 2016-05-03 06:16:45<br>num.completed.cum: 323","EndDate: 2016-05-03 06:19:30<br>num.completed.cum: 324","EndDate: 2016-05-03 06:26:15<br>num.completed.cum: 325","EndDate: 2016-05-03 06:29:14<br>num.completed.cum: 326","EndDate: 2016-05-03 06:32:16<br>num.completed.cum: 327","EndDate: 2016-05-03 06:37:43<br>num.completed.cum: 328","EndDate: 2016-05-03 06:39:19<br>num.completed.cum: 329","EndDate: 2016-05-03 06:40:50<br>num.completed.cum: 330","EndDate: 2016-05-03 06:53:30<br>num.completed.cum: 331","EndDate: 2016-05-03 07:03:15<br>num.completed.cum: 332","EndDate: 2016-05-03 07:39:12<br>num.completed.cum: 333","EndDate: 2016-05-03 07:43:30<br>num.completed.cum: 334","EndDate: 2016-05-03 07:49:13<br>num.completed.cum: 335","EndDate: 2016-05-03 07:54:06<br>num.completed.cum: 336","EndDate: 2016-05-03 08:17:34<br>num.completed.cum: 337","EndDate: 2016-05-03 08:23:52<br>num.completed.cum: 338","EndDate: 2016-05-03 08:56:48<br>num.completed.cum: 339","EndDate: 2016-05-03 09:07:37<br>num.completed.cum: 340","EndDate: 2016-05-03 10:22:45<br>num.completed.cum: 341","EndDate: 2016-05-03 11:02:56<br>num.completed.cum: 342","EndDate: 2016-05-03 11:34:05<br>num.completed.cum: 343","EndDate: 2016-05-03 11:38:17<br>num.completed.cum: 344","EndDate: 2016-05-03 11:40:08<br>num.completed.cum: 345","EndDate: 2016-05-03 11:51:05<br>num.completed.cum: 346","EndDate: 2016-05-03 11:54:25<br>num.completed.cum: 347","EndDate: 2016-05-03 11:59:44<br>num.completed.cum: 348","EndDate: 2016-05-03 12:01:39<br>num.completed.cum: 349","EndDate: 2016-05-03 12:05:19<br>num.completed.cum: 350","EndDate: 2016-05-03 12:10:47<br>num.completed.cum: 351","EndDate: 2016-05-03 12:12:56<br>num.completed.cum: 352","EndDate: 2016-05-03 12:20:17<br>num.completed.cum: 353","EndDate: 2016-05-03 12:22:24<br>num.completed.cum: 354","EndDate: 2016-05-03 12:39:37<br>num.completed.cum: 355","EndDate: 2016-05-03 12:56:48<br>num.completed.cum: 356","EndDate: 2016-05-03 13:23:26<br>num.completed.cum: 357","EndDate: 2016-05-03 13:24:08<br>num.completed.cum: 358","EndDate: 2016-05-03 13:42:02<br>num.completed.cum: 359","EndDate: 2016-05-03 14:18:39<br>num.completed.cum: 360","EndDate: 2016-05-03 14:52:06<br>num.completed.cum: 361","EndDate: 2016-05-03 15:35:26<br>num.completed.cum: 362","EndDate: 2016-05-03 16:06:44<br>num.completed.cum: 363","EndDate: 2016-05-03 17:05:45<br>num.completed.cum: 364","EndDate: 2016-05-03 17:39:31<br>num.completed.cum: 365","EndDate: 2016-05-03 20:05:00<br>num.completed.cum: 366","EndDate: 2016-05-03 20:38:33<br>num.completed.cum: 367","EndDate: 2016-05-03 20:43:05<br>num.completed.cum: 368","EndDate: 2016-05-03 21:10:24<br>num.completed.cum: 369","EndDate: 2016-05-03 21:18:09<br>num.completed.cum: 370","EndDate: 2016-05-03 21:50:20<br>num.completed.cum: 371","EndDate: 2016-05-03 22:25:48<br>num.completed.cum: 372","EndDate: 2016-05-03 22:40:36<br>num.completed.cum: 373","EndDate: 2016-05-03 23:26:26<br>num.completed.cum: 374","EndDate: 2016-05-04 00:04:51<br>num.completed.cum: 375","EndDate: 2016-05-04 00:19:16<br>num.completed.cum: 376","EndDate: 2016-05-04 00:46:18<br>num.completed.cum: 377","EndDate: 2016-05-04 01:27:24<br>num.completed.cum: 378","EndDate: 2016-05-04 02:14:52<br>num.completed.cum: 379","EndDate: 2016-05-04 02:22:44<br>num.completed.cum: 380","EndDate: 2016-05-04 03:18:39<br>num.completed.cum: 381","EndDate: 2016-05-04 03:33:07<br>num.completed.cum: 382","EndDate: 2016-05-04 05:04:37<br>num.completed.cum: 383","EndDate: 2016-05-04 05:13:23<br>num.completed.cum: 384","EndDate: 2016-05-04 05:24:03<br>num.completed.cum: 385","EndDate: 2016-05-04 06:45:16<br>num.completed.cum: 386","EndDate: 2016-05-04 07:02:52<br>num.completed.cum: 387","EndDate: 2016-05-04 07:07:08<br>num.completed.cum: 388","EndDate: 2016-05-04 07:16:16<br>num.completed.cum: 389","EndDate: 2016-05-04 07:27:16<br>num.completed.cum: 390","EndDate: 2016-05-04 08:04:27<br>num.completed.cum: 391","EndDate: 2016-05-04 08:09:12<br>num.completed.cum: 392","EndDate: 2016-05-04 08:27:31<br>num.completed.cum: 393","EndDate: 2016-05-04 09:36:32<br>num.completed.cum: 394","EndDate: 2016-05-04 10:24:50<br>num.completed.cum: 395","EndDate: 2016-05-04 10:30:19<br>num.completed.cum: 396","EndDate: 2016-05-04 12:08:19<br>num.completed.cum: 397","EndDate: 2016-05-04 12:11:21<br>num.completed.cum: 398","EndDate: 2016-05-04 13:14:39<br>num.completed.cum: 399","EndDate: 2016-05-04 13:58:48<br>num.completed.cum: 400","EndDate: 2016-05-04 14:42:02<br>num.completed.cum: 401","EndDate: 2016-05-04 18:06:46<br>num.completed.cum: 402","EndDate: 2016-05-04 18:43:41<br>num.completed.cum: 403","EndDate: 2016-05-04 21:09:59<br>num.completed.cum: 404","EndDate: 2016-05-05 01:31:58<br>num.completed.cum: 405","EndDate: 2016-05-05 03:23:20<br>num.completed.cum: 406","EndDate: 2016-05-05 03:52:24<br>num.completed.cum: 407","EndDate: 2016-05-05 04:20:25<br>num.completed.cum: 408","EndDate: 2016-05-05 05:24:42<br>num.completed.cum: 409","EndDate: 2016-05-05 07:27:06<br>num.completed.cum: 410","EndDate: 2016-05-05 08:29:54<br>num.completed.cum: 411","EndDate: 2016-05-05 08:37:55<br>num.completed.cum: 412","EndDate: 2016-05-05 09:24:14<br>num.completed.cum: 413","EndDate: 2016-05-05 09:43:44<br>num.completed.cum: 414","EndDate: 2016-05-05 10:15:18<br>num.completed.cum: 415","EndDate: 2016-05-05 10:28:00<br>num.completed.cum: 416","EndDate: 2016-05-05 10:30:21<br>num.completed.cum: 417","EndDate: 2016-05-05 11:31:20<br>num.completed.cum: 418","EndDate: 2016-05-05 15:21:16<br>num.completed.cum: 419","EndDate: 2016-05-05 16:02:38<br>num.completed.cum: 420","EndDate: 2016-05-05 16:10:40<br>num.completed.cum: 421","EndDate: 2016-05-05 16:35:32<br>num.completed.cum: 422","EndDate: 2016-05-05 22:32:39<br>num.completed.cum: 423","EndDate: 2016-05-06 00:00:35<br>num.completed.cum: 424","EndDate: 2016-05-06 03:01:23<br>num.completed.cum: 425","EndDate: 2016-05-06 04:44:05<br>num.completed.cum: 426","EndDate: 2016-05-06 04:56:23<br>num.completed.cum: 427","EndDate: 2016-05-06 05:45:06<br>num.completed.cum: 428","EndDate: 2016-05-06 05:47:44<br>num.completed.cum: 429","EndDate: 2016-05-06 07:07:20<br>num.completed.cum: 430","EndDate: 2016-05-06 15:44:10<br>num.completed.cum: 431","EndDate: 2016-05-06 18:24:52<br>num.completed.cum: 432","EndDate: 2016-05-07 08:15:57<br>num.completed.cum: 433","EndDate: 2016-05-07 09:25:18<br>num.completed.cum: 434","EndDate: 2016-05-07 11:47:26<br>num.completed.cum: 435","EndDate: 2016-05-07 18:13:39<br>num.completed.cum: 436","EndDate: 2016-05-07 21:49:27<br>num.completed.cum: 437","EndDate: 2016-05-08 06:49:33<br>num.completed.cum: 438","EndDate: 2016-05-08 08:07:39<br>num.completed.cum: 439","EndDate: 2016-05-08 17:21:14<br>num.completed.cum: 440","EndDate: 2016-05-08 23:28:14<br>num.completed.cum: 441","EndDate: 2016-05-09 00:31:49<br>num.completed.cum: 442","EndDate: 2016-05-09 03:55:59<br>num.completed.cum: 443","EndDate: 2016-05-09 04:55:34<br>num.completed.cum: 444","EndDate: 2016-05-09 06:14:30<br>num.completed.cum: 445","EndDate: 2016-05-09 06:20:53<br>num.completed.cum: 446","EndDate: 2016-05-09 12:57:02<br>num.completed.cum: 447","EndDate: 2016-05-09 14:44:06<br>num.completed.cum: 448","EndDate: 2016-05-09 17:03:07<br>num.completed.cum: 449","EndDate: 2016-05-09 22:20:21<br>num.completed.cum: 450","EndDate: 2016-05-09 22:53:38<br>num.completed.cum: 451","EndDate: 2016-05-10 00:44:30<br>num.completed.cum: 452","EndDate: 2016-05-10 01:10:11<br>num.completed.cum: 453","EndDate: 2016-05-10 01:17:21<br>num.completed.cum: 454","EndDate: 2016-05-10 02:13:41<br>num.completed.cum: 455","EndDate: 2016-05-10 04:51:39<br>num.completed.cum: 456","EndDate: 2016-05-10 04:58:18<br>num.completed.cum: 457","EndDate: 2016-05-10 05:43:19<br>num.completed.cum: 458","EndDate: 2016-05-10 05:51:02<br>num.completed.cum: 459","EndDate: 2016-05-10 05:56:31<br>num.completed.cum: 460","EndDate: 2016-05-10 05:59:26<br>num.completed.cum: 461","EndDate: 2016-05-10 06:12:56<br>num.completed.cum: 462","EndDate: 2016-05-10 06:20:31<br>num.completed.cum: 463","EndDate: 2016-05-10 06:28:29<br>num.completed.cum: 464","EndDate: 2016-05-10 06:33:56<br>num.completed.cum: 465","EndDate: 2016-05-10 06:47:48<br>num.completed.cum: 466","EndDate: 2016-05-10 07:20:01<br>num.completed.cum: 467","EndDate: 2016-05-10 07:20:07<br>num.completed.cum: 468","EndDate: 2016-05-10 07:20:45<br>num.completed.cum: 469","EndDate: 2016-05-10 07:24:54<br>num.completed.cum: 470","EndDate: 2016-05-10 07:42:51<br>num.completed.cum: 471","EndDate: 2016-05-10 07:47:48<br>num.completed.cum: 472","EndDate: 2016-05-10 07:54:15<br>num.completed.cum: 473","EndDate: 2016-05-10 07:54:44<br>num.completed.cum: 474","EndDate: 2016-05-10 08:02:16<br>num.completed.cum: 475","EndDate: 2016-05-10 08:02:19<br>num.completed.cum: 476","EndDate: 2016-05-10 08:04:45<br>num.completed.cum: 477","EndDate: 2016-05-10 08:09:26<br>num.completed.cum: 478","EndDate: 2016-05-10 08:14:20<br>num.completed.cum: 479","EndDate: 2016-05-10 08:18:56<br>num.completed.cum: 480","EndDate: 2016-05-10 08:27:21<br>num.completed.cum: 481","EndDate: 2016-05-10 08:34:06<br>num.completed.cum: 482","EndDate: 2016-05-10 08:38:23<br>num.completed.cum: 483","EndDate: 2016-05-10 08:39:28<br>num.completed.cum: 484","EndDate: 2016-05-10 08:53:29<br>num.completed.cum: 485","EndDate: 2016-05-10 09:05:06<br>num.completed.cum: 486","EndDate: 2016-05-10 09:05:12<br>num.completed.cum: 487","EndDate: 2016-05-10 09:05:53<br>num.completed.cum: 488","EndDate: 2016-05-10 09:10:52<br>num.completed.cum: 489","EndDate: 2016-05-10 09:11:16<br>num.completed.cum: 490","EndDate: 2016-05-10 09:12:34<br>num.completed.cum: 491","EndDate: 2016-05-10 09:14:24<br>num.completed.cum: 492","EndDate: 2016-05-10 09:30:51<br>num.completed.cum: 493","EndDate: 2016-05-10 09:34:44<br>num.completed.cum: 494","EndDate: 2016-05-10 09:42:55<br>num.completed.cum: 495","EndDate: 2016-05-10 09:57:23<br>num.completed.cum: 496","EndDate: 2016-05-10 10:03:39<br>num.completed.cum: 497","EndDate: 2016-05-10 11:11:23<br>num.completed.cum: 498","EndDate: 2016-05-10 11:11:50<br>num.completed.cum: 499","EndDate: 2016-05-10 11:21:25<br>num.completed.cum: 500","EndDate: 2016-05-10 11:31:59<br>num.completed.cum: 501","EndDate: 2016-05-10 11:38:24<br>num.completed.cum: 502","EndDate: 2016-05-10 11:41:09<br>num.completed.cum: 503","EndDate: 2016-05-10 12:00:34<br>num.completed.cum: 504","EndDate: 2016-05-10 12:04:45<br>num.completed.cum: 505","EndDate: 2016-05-10 12:17:46<br>num.completed.cum: 506","EndDate: 2016-05-10 12:24:04<br>num.completed.cum: 507","EndDate: 2016-05-10 12:29:43<br>num.completed.cum: 508","EndDate: 2016-05-10 12:34:58<br>num.completed.cum: 509","EndDate: 2016-05-10 12:40:48<br>num.completed.cum: 510","EndDate: 2016-05-10 12:52:43<br>num.completed.cum: 511","EndDate: 2016-05-10 12:57:50<br>num.completed.cum: 512","EndDate: 2016-05-10 13:28:26<br>num.completed.cum: 513","EndDate: 2016-05-10 13:37:06<br>num.completed.cum: 514","EndDate: 2016-05-10 13:45:23<br>num.completed.cum: 515","EndDate: 2016-05-10 14:22:23<br>num.completed.cum: 516","EndDate: 2016-05-10 14:33:16<br>num.completed.cum: 517","EndDate: 2016-05-10 14:41:06<br>num.completed.cum: 518","EndDate: 2016-05-10 14:50:17<br>num.completed.cum: 519","EndDate: 2016-05-10 15:06:21<br>num.completed.cum: 520","EndDate: 2016-05-10 15:10:38<br>num.completed.cum: 521","EndDate: 2016-05-10 16:03:35<br>num.completed.cum: 522","EndDate: 2016-05-10 17:29:15<br>num.completed.cum: 523","EndDate: 2016-05-10 17:51:16<br>num.completed.cum: 524","EndDate: 2016-05-10 17:54:32<br>num.completed.cum: 525","EndDate: 2016-05-10 17:56:15<br>num.completed.cum: 526","EndDate: 2016-05-10 18:29:42<br>num.completed.cum: 527","EndDate: 2016-05-10 19:08:02<br>num.completed.cum: 528","EndDate: 2016-05-10 19:37:05<br>num.completed.cum: 529","EndDate: 2016-05-10 21:04:44<br>num.completed.cum: 530","EndDate: 2016-05-10 22:02:49<br>num.completed.cum: 531","EndDate: 2016-05-10 22:11:13<br>num.completed.cum: 532","EndDate: 2016-05-10 22:20:47<br>num.completed.cum: 533","EndDate: 2016-05-10 22:46:14<br>num.completed.cum: 534","EndDate: 2016-05-10 22:53:03<br>num.completed.cum: 535","EndDate: 2016-05-10 23:19:18<br>num.completed.cum: 536","EndDate: 2016-05-10 23:55:48<br>num.completed.cum: 537","EndDate: 2016-05-11 00:01:36<br>num.completed.cum: 538","EndDate: 2016-05-11 00:14:15<br>num.completed.cum: 539","EndDate: 2016-05-11 00:21:20<br>num.completed.cum: 540","EndDate: 2016-05-11 00:22:27<br>num.completed.cum: 541","EndDate: 2016-05-11 00:29:17<br>num.completed.cum: 542","EndDate: 2016-05-11 00:40:14<br>num.completed.cum: 543","EndDate: 2016-05-11 00:49:22<br>num.completed.cum: 544","EndDate: 2016-05-11 00:49:40<br>num.completed.cum: 545","EndDate: 2016-05-11 01:13:54<br>num.completed.cum: 546","EndDate: 2016-05-11 01:18:17<br>num.completed.cum: 547","EndDate: 2016-05-11 01:20:30<br>num.completed.cum: 548","EndDate: 2016-05-11 01:37:15<br>num.completed.cum: 549","EndDate: 2016-05-11 02:14:44<br>num.completed.cum: 550","EndDate: 2016-05-11 02:30:16<br>num.completed.cum: 551","EndDate: 2016-05-11 02:48:10<br>num.completed.cum: 552","EndDate: 2016-05-11 03:01:36<br>num.completed.cum: 553","EndDate: 2016-05-11 03:22:33<br>num.completed.cum: 554","EndDate: 2016-05-11 03:23:25<br>num.completed.cum: 555","EndDate: 2016-05-11 04:00:20<br>num.completed.cum: 556","EndDate: 2016-05-11 04:04:46<br>num.completed.cum: 557","EndDate: 2016-05-11 04:07:50<br>num.completed.cum: 558","EndDate: 2016-05-11 04:08:36<br>num.completed.cum: 559","EndDate: 2016-05-11 04:22:25<br>num.completed.cum: 560","EndDate: 2016-05-11 05:10:00<br>num.completed.cum: 561","EndDate: 2016-05-11 05:23:53<br>num.completed.cum: 562","EndDate: 2016-05-11 05:59:38<br>num.completed.cum: 563","EndDate: 2016-05-11 05:59:40<br>num.completed.cum: 564","EndDate: 2016-05-11 06:23:31<br>num.completed.cum: 565","EndDate: 2016-05-11 06:24:58<br>num.completed.cum: 566","EndDate: 2016-05-11 07:06:20<br>num.completed.cum: 567","EndDate: 2016-05-11 07:16:44<br>num.completed.cum: 568","EndDate: 2016-05-11 07:26:04<br>num.completed.cum: 569","EndDate: 2016-05-11 07:54:57<br>num.completed.cum: 570","EndDate: 2016-05-11 07:56:59<br>num.completed.cum: 571","EndDate: 2016-05-11 08:07:44<br>num.completed.cum: 572","EndDate: 2016-05-11 08:19:57<br>num.completed.cum: 573","EndDate: 2016-05-11 08:57:35<br>num.completed.cum: 574","EndDate: 2016-05-11 08:58:05<br>num.completed.cum: 575","EndDate: 2016-05-11 09:06:42<br>num.completed.cum: 576","EndDate: 2016-05-11 09:28:43<br>num.completed.cum: 577","EndDate: 2016-05-11 10:07:47<br>num.completed.cum: 578","EndDate: 2016-05-11 11:13:22<br>num.completed.cum: 579","EndDate: 2016-05-11 11:48:28<br>num.completed.cum: 580","EndDate: 2016-05-11 12:11:03<br>num.completed.cum: 581","EndDate: 2016-05-11 12:41:52<br>num.completed.cum: 582","EndDate: 2016-05-11 13:02:31<br>num.completed.cum: 583","EndDate: 2016-05-11 14:02:02<br>num.completed.cum: 584","EndDate: 2016-05-11 14:54:41<br>num.completed.cum: 585","EndDate: 2016-05-11 15:55:33<br>num.completed.cum: 586","EndDate: 2016-05-11 18:10:59<br>num.completed.cum: 587","EndDate: 2016-05-11 18:37:38<br>num.completed.cum: 588","EndDate: 2016-05-11 22:30:11<br>num.completed.cum: 589","EndDate: 2016-05-11 23:53:03<br>num.completed.cum: 590","EndDate: 2016-05-12 00:04:43<br>num.completed.cum: 591","EndDate: 2016-05-12 00:23:35<br>num.completed.cum: 592","EndDate: 2016-05-12 03:01:32<br>num.completed.cum: 593","EndDate: 2016-05-12 03:03:45<br>num.completed.cum: 594","EndDate: 2016-05-12 03:25:55<br>num.completed.cum: 595","EndDate: 2016-05-12 04:15:56<br>num.completed.cum: 596","EndDate: 2016-05-12 07:21:52<br>num.completed.cum: 597","EndDate: 2016-05-12 08:44:24<br>num.completed.cum: 598","EndDate: 2016-05-12 08:47:32<br>num.completed.cum: 599","EndDate: 2016-05-12 09:01:29<br>num.completed.cum: 600","EndDate: 2016-05-12 09:45:39<br>num.completed.cum: 601","EndDate: 2016-05-12 10:17:12<br>num.completed.cum: 602","EndDate: 2016-05-12 10:24:59<br>num.completed.cum: 603","EndDate: 2016-05-12 10:40:00<br>num.completed.cum: 604","EndDate: 2016-05-12 11:48:10<br>num.completed.cum: 605","EndDate: 2016-05-12 15:54:56<br>num.completed.cum: 606","EndDate: 2016-05-12 17:35:22<br>num.completed.cum: 607","EndDate: 2016-05-12 17:40:08<br>num.completed.cum: 608","EndDate: 2016-05-12 17:50:04<br>num.completed.cum: 609","EndDate: 2016-05-12 23:13:04<br>num.completed.cum: 610","EndDate: 2016-05-12 23:31:32<br>num.completed.cum: 611","EndDate: 2016-05-13 00:23:25<br>num.completed.cum: 612","EndDate: 2016-05-13 02:14:35<br>num.completed.cum: 613","EndDate: 2016-05-13 02:42:17<br>num.completed.cum: 614","EndDate: 2016-05-13 03:06:17<br>num.completed.cum: 615","EndDate: 2016-05-13 03:06:52<br>num.completed.cum: 616","EndDate: 2016-05-13 04:34:03<br>num.completed.cum: 617","EndDate: 2016-05-13 04:42:45<br>num.completed.cum: 618","EndDate: 2016-05-13 05:15:08<br>num.completed.cum: 619","EndDate: 2016-05-13 05:15:42<br>num.completed.cum: 620","EndDate: 2016-05-13 06:45:35<br>num.completed.cum: 621","EndDate: 2016-05-13 07:24:53<br>num.completed.cum: 622","EndDate: 2016-05-13 09:47:53<br>num.completed.cum: 623","EndDate: 2016-05-13 10:14:36<br>num.completed.cum: 624","EndDate: 2016-05-13 10:56:57<br>num.completed.cum: 625","EndDate: 2016-05-13 11:28:32<br>num.completed.cum: 626","EndDate: 2016-05-13 11:39:46<br>num.completed.cum: 627","EndDate: 2016-05-14 07:21:46<br>num.completed.cum: 628","EndDate: 2016-05-15 00:41:20<br>num.completed.cum: 629","EndDate: 2016-05-15 03:28:47<br>num.completed.cum: 630","EndDate: 2016-05-15 03:35:04<br>num.completed.cum: 631","EndDate: 2016-05-15 04:17:30<br>num.completed.cum: 632","EndDate: 2016-05-15 06:07:25<br>num.completed.cum: 633","EndDate: 2016-05-15 08:15:59<br>num.completed.cum: 634","EndDate: 2016-05-15 12:37:21<br>num.completed.cum: 635","EndDate: 2016-05-15 20:37:23<br>num.completed.cum: 636","EndDate: 2016-05-16 00:17:47<br>num.completed.cum: 637","EndDate: 2016-05-16 00:38:48<br>num.completed.cum: 638","EndDate: 2016-05-16 01:16:40<br>num.completed.cum: 639","EndDate: 2016-05-16 03:43:31<br>num.completed.cum: 640","EndDate: 2016-05-16 07:43:41<br>num.completed.cum: 641","EndDate: 2016-05-16 07:59:10<br>num.completed.cum: 642","EndDate: 2016-05-16 10:03:16<br>num.completed.cum: 643","EndDate: 2016-05-16 22:27:33<br>num.completed.cum: 644","EndDate: 2016-05-17 02:09:52<br>num.completed.cum: 645","EndDate: 2016-05-17 02:57:50<br>num.completed.cum: 646","EndDate: 2016-05-17 03:06:11<br>num.completed.cum: 647","EndDate: 2016-05-17 03:44:26<br>num.completed.cum: 648","EndDate: 2016-05-17 04:52:24<br>num.completed.cum: 649","EndDate: 2016-05-17 04:55:11<br>num.completed.cum: 650","EndDate: 2016-05-17 04:55:34<br>num.completed.cum: 651","EndDate: 2016-05-17 06:16:35<br>num.completed.cum: 652","EndDate: 2016-05-17 08:18:51<br>num.completed.cum: 653","EndDate: 2016-05-17 08:45:00<br>num.completed.cum: 654","EndDate: 2016-05-17 11:45:15<br>num.completed.cum: 655","EndDate: 2016-05-17 15:30:42<br>num.completed.cum: 656","EndDate: 2016-05-17 20:57:34<br>num.completed.cum: 657","EndDate: 2016-05-17 23:38:32<br>num.completed.cum: 658","EndDate: 2016-05-18 01:37:07<br>num.completed.cum: 659","EndDate: 2016-05-18 03:53:37<br>num.completed.cum: 660","EndDate: 2016-05-18 05:44:26<br>num.completed.cum: 661","EndDate: 2016-05-18 08:15:21<br>num.completed.cum: 662","EndDate: 2016-05-18 11:03:53<br>num.completed.cum: 663","EndDate: 2016-05-18 15:16:48<br>num.completed.cum: 664","EndDate: 2016-05-18 18:47:01<br>num.completed.cum: 665","EndDate: 2016-05-19 00:24:17<br>num.completed.cum: 666","EndDate: 2016-05-19 12:07:57<br>num.completed.cum: 667","EndDate: 2016-05-19 16:05:01<br>num.completed.cum: 668","EndDate: 2016-05-20 09:14:07<br>num.completed.cum: 669","EndDate: 2016-05-20 15:36:42<br>num.completed.cum: 670","EndDate: 2016-05-23 07:33:52<br>num.completed.cum: 671","EndDate: 2016-05-23 12:40:07<br>num.completed.cum: 672","EndDate: 2016-05-24 19:47:18<br>num.completed.cum: 673","EndDate: 2016-05-26 01:04:06<br>num.completed.cum: 674","EndDate: 2016-05-28 06:10:28<br>num.completed.cum: 675","EndDate: 2016-05-30 18:41:40<br>num.completed.cum: 676","EndDate: 2016-05-31 23:51:20<br>num.completed.cum: 677","EndDate: 2016-06-02 14:06:45<br>num.completed.cum: 678","EndDate: 2016-06-06 00:09:29<br>num.completed.cum: 679","EndDate: 2016-06-06 11:29:08<br>num.completed.cum: 680","EndDate: 2016-06-06 11:31:11<br>num.completed.cum: 681","EndDate: 2016-06-06 11:46:01<br>num.completed.cum: 682","EndDate: 2016-06-06 11:57:07<br>num.completed.cum: 683","EndDate: 2016-06-06 12:20:55<br>num.completed.cum: 684","EndDate: 2016-06-06 12:21:07<br>num.completed.cum: 685","EndDate: 2016-06-06 12:28:08<br>num.completed.cum: 686","EndDate: 2016-06-06 12:34:35<br>num.completed.cum: 687","EndDate: 2016-06-06 12:34:47<br>num.completed.cum: 688","EndDate: 2016-06-06 12:39:10<br>num.completed.cum: 689","EndDate: 2016-06-06 13:04:17<br>num.completed.cum: 690","EndDate: 2016-06-06 13:25:11<br>num.completed.cum: 691","EndDate: 2016-06-06 13:26:10<br>num.completed.cum: 692","EndDate: 2016-06-06 13:26:33<br>num.completed.cum: 693","EndDate: 2016-06-06 13:53:55<br>num.completed.cum: 694","EndDate: 2016-06-06 14:02:14<br>num.completed.cum: 695","EndDate: 2016-06-06 14:35:42<br>num.completed.cum: 696","EndDate: 2016-06-06 14:40:11<br>num.completed.cum: 697","EndDate: 2016-06-06 14:41:39<br>num.completed.cum: 698","EndDate: 2016-06-06 15:09:50<br>num.completed.cum: 699","EndDate: 2016-06-06 15:35:40<br>num.completed.cum: 700","EndDate: 2016-06-06 16:26:32<br>num.completed.cum: 701","EndDate: 2016-06-06 17:00:49<br>num.completed.cum: 702","EndDate: 2016-06-06 17:08:41<br>num.completed.cum: 703","EndDate: 2016-06-06 17:10:01<br>num.completed.cum: 704","EndDate: 2016-06-06 17:23:16<br>num.completed.cum: 705","EndDate: 2016-06-06 18:09:47<br>num.completed.cum: 706","EndDate: 2016-06-06 18:44:44<br>num.completed.cum: 707","EndDate: 2016-06-06 18:51:05<br>num.completed.cum: 708","EndDate: 2016-06-06 19:09:02<br>num.completed.cum: 709","EndDate: 2016-06-06 19:24:57<br>num.completed.cum: 710","EndDate: 2016-06-06 19:37:19<br>num.completed.cum: 711","EndDate: 2016-06-06 21:13:00<br>num.completed.cum: 712","EndDate: 2016-06-06 23:06:04<br>num.completed.cum: 713","EndDate: 2016-06-06 23:18:37<br>num.completed.cum: 714","EndDate: 2016-06-06 23:22:22<br>num.completed.cum: 715","EndDate: 2016-06-06 23:36:26<br>num.completed.cum: 716","EndDate: 2016-06-06 23:37:04<br>num.completed.cum: 717","EndDate: 2016-06-06 23:45:44<br>num.completed.cum: 718","EndDate: 2016-06-07 00:05:33<br>num.completed.cum: 719","EndDate: 2016-06-07 00:07:00<br>num.completed.cum: 720","EndDate: 2016-06-07 00:42:23<br>num.completed.cum: 721","EndDate: 2016-06-07 00:47:40<br>num.completed.cum: 722","EndDate: 2016-06-07 01:02:14<br>num.completed.cum: 723","EndDate: 2016-06-07 01:12:16<br>num.completed.cum: 724","EndDate: 2016-06-07 01:15:40<br>num.completed.cum: 725","EndDate: 2016-06-07 01:40:25<br>num.completed.cum: 726","EndDate: 2016-06-07 01:47:23<br>num.completed.cum: 727","EndDate: 2016-06-07 01:49:29<br>num.completed.cum: 728","EndDate: 2016-06-07 01:55:40<br>num.completed.cum: 729","EndDate: 2016-06-07 02:07:07<br>num.completed.cum: 730","EndDate: 2016-06-07 02:09:34<br>num.completed.cum: 731","EndDate: 2016-06-07 02:18:59<br>num.completed.cum: 732","EndDate: 2016-06-07 02:27:20<br>num.completed.cum: 733","EndDate: 2016-06-07 02:44:58<br>num.completed.cum: 734","EndDate: 2016-06-07 02:56:22<br>num.completed.cum: 735","EndDate: 2016-06-07 02:59:49<br>num.completed.cum: 736","EndDate: 2016-06-07 03:26:45<br>num.completed.cum: 737","EndDate: 2016-06-07 03:31:15<br>num.completed.cum: 738","EndDate: 2016-06-07 03:41:09<br>num.completed.cum: 739","EndDate: 2016-06-07 03:44:17<br>num.completed.cum: 740","EndDate: 2016-06-07 03:56:42<br>num.completed.cum: 741","EndDate: 2016-06-07 04:06:58<br>num.completed.cum: 742","EndDate: 2016-06-07 05:18:15<br>num.completed.cum: 743","EndDate: 2016-06-07 06:11:33<br>num.completed.cum: 744","EndDate: 2016-06-07 06:23:19<br>num.completed.cum: 745","EndDate: 2016-06-07 08:02:21<br>num.completed.cum: 746","EndDate: 2016-06-07 08:15:29<br>num.completed.cum: 747","EndDate: 2016-06-07 08:48:30<br>num.completed.cum: 748","EndDate: 2016-06-07 08:59:54<br>num.completed.cum: 749","EndDate: 2016-06-07 09:12:27<br>num.completed.cum: 750","EndDate: 2016-06-07 09:23:47<br>num.completed.cum: 751","EndDate: 2016-06-07 10:16:02<br>num.completed.cum: 752","EndDate: 2016-06-07 10:33:27<br>num.completed.cum: 753","EndDate: 2016-06-07 13:41:16<br>num.completed.cum: 754","EndDate: 2016-06-07 15:13:12<br>num.completed.cum: 755","EndDate: 2016-06-07 16:43:15<br>num.completed.cum: 756","EndDate: 2016-06-07 17:43:49<br>num.completed.cum: 757","EndDate: 2016-06-07 18:15:37<br>num.completed.cum: 758","EndDate: 2016-06-07 18:29:11<br>num.completed.cum: 759","EndDate: 2016-06-07 18:52:04<br>num.completed.cum: 760","EndDate: 2016-06-07 19:21:36<br>num.completed.cum: 761","EndDate: 2016-06-07 20:02:52<br>num.completed.cum: 762","EndDate: 2016-06-07 22:11:58<br>num.completed.cum: 763","EndDate: 2016-06-07 23:14:26<br>num.completed.cum: 764","EndDate: 2016-06-08 00:11:55<br>num.completed.cum: 765","EndDate: 2016-06-08 00:13:54<br>num.completed.cum: 766","EndDate: 2016-06-08 01:28:34<br>num.completed.cum: 767","EndDate: 2016-06-08 02:28:26<br>num.completed.cum: 768","EndDate: 2016-06-08 03:26:56<br>num.completed.cum: 769","EndDate: 2016-06-08 04:44:01<br>num.completed.cum: 770","EndDate: 2016-06-08 05:23:01<br>num.completed.cum: 771","EndDate: 2016-06-08 06:22:50<br>num.completed.cum: 772","EndDate: 2016-06-08 06:27:58<br>num.completed.cum: 773","EndDate: 2016-06-08 07:20:50<br>num.completed.cum: 774","EndDate: 2016-06-08 08:18:10<br>num.completed.cum: 775","EndDate: 2016-06-08 09:31:41<br>num.completed.cum: 776","EndDate: 2016-06-08 09:48:23<br>num.completed.cum: 777","EndDate: 2016-06-08 10:20:11<br>num.completed.cum: 778","EndDate: 2016-06-08 10:57:16<br>num.completed.cum: 779","EndDate: 2016-06-08 12:46:07<br>num.completed.cum: 780","EndDate: 2016-06-08 12:56:18<br>num.completed.cum: 781","EndDate: 2016-06-08 13:55:39<br>num.completed.cum: 782","EndDate: 2016-06-08 17:19:29<br>num.completed.cum: 783","EndDate: 2016-06-08 23:57:09<br>num.completed.cum: 784","EndDate: 2016-06-09 00:53:41<br>num.completed.cum: 785","EndDate: 2016-06-09 01:18:49<br>num.completed.cum: 786","EndDate: 2016-06-09 03:31:14<br>num.completed.cum: 787","EndDate: 2016-06-09 06:11:34<br>num.completed.cum: 788","EndDate: 2016-06-09 06:19:47<br>num.completed.cum: 789","EndDate: 2016-06-09 07:36:43<br>num.completed.cum: 790","EndDate: 2016-06-09 11:20:59<br>num.completed.cum: 791","EndDate: 2016-06-09 11:29:58<br>num.completed.cum: 792","EndDate: 2016-06-09 14:05:12<br>num.completed.cum: 793","EndDate: 2016-06-09 14:45:25<br>num.completed.cum: 794","EndDate: 2016-06-09 16:43:02<br>num.completed.cum: 795","EndDate: 2016-06-09 17:12:28<br>num.completed.cum: 796","EndDate: 2016-06-09 20:14:11<br>num.completed.cum: 797","EndDate: 2016-06-09 22:46:49<br>num.completed.cum: 798","EndDate: 2016-06-10 06:14:51<br>num.completed.cum: 799","EndDate: 2016-06-10 06:19:09<br>num.completed.cum: 800","EndDate: 2016-06-10 06:36:56<br>num.completed.cum: 801","EndDate: 2016-06-10 08:02:19<br>num.completed.cum: 802","EndDate: 2016-06-10 08:37:14<br>num.completed.cum: 803","EndDate: 2016-06-10 08:53:20<br>num.completed.cum: 804","EndDate: 2016-06-10 12:45:09<br>num.completed.cum: 805","EndDate: 2016-06-10 13:29:23<br>num.completed.cum: 806","EndDate: 2016-06-10 16:52:24<br>num.completed.cum: 807","EndDate: 2016-06-10 17:23:40<br>num.completed.cum: 808","EndDate: 2016-06-11 01:15:06<br>num.completed.cum: 809","EndDate: 2016-06-11 08:31:37<br>num.completed.cum: 810","EndDate: 2016-06-11 10:11:53<br>num.completed.cum: 811","EndDate: 2016-06-11 11:27:23<br>num.completed.cum: 812","EndDate: 2016-06-12 02:45:57<br>num.completed.cum: 813","EndDate: 2016-06-12 07:18:42<br>num.completed.cum: 814","EndDate: 2016-06-13 04:32:26<br>num.completed.cum: 815","EndDate: 2016-06-13 05:01:05<br>num.completed.cum: 816","EndDate: 2016-06-14 09:14:49<br>num.completed.cum: 817","EndDate: 2016-06-14 09:50:05<br>num.completed.cum: 818","EndDate: 2016-06-15 00:48:32<br>num.completed.cum: 819","EndDate: 2016-06-15 04:52:25<br>num.completed.cum: 820","EndDate: 2016-06-15 05:35:24<br>num.completed.cum: 821","EndDate: 2016-06-15 06:35:36<br>num.completed.cum: 822","EndDate: 2016-06-15 07:08:45<br>num.completed.cum: 823","EndDate: 2016-06-15 10:15:56<br>num.completed.cum: 824","EndDate: 2016-06-16 09:09:48<br>num.completed.cum: 825","EndDate: 2016-06-16 19:41:50<br>num.completed.cum: 826","EndDate: 2016-06-17 08:47:19<br>num.completed.cum: 827","EndDate: 2016-06-17 21:30:12<br>num.completed.cum: 828","EndDate: 2016-06-17 23:13:08<br>num.completed.cum: 829","EndDate: 2016-06-19 02:47:44<br>num.completed.cum: 830","EndDate: 2016-06-20 00:50:12<br>num.completed.cum: 831","EndDate: 2016-06-20 13:50:10<br>num.completed.cum: 832","EndDate: 2016-06-20 15:08:52<br>num.completed.cum: 833","EndDate: 2016-06-21 09:42:07<br>num.completed.cum: 834","EndDate: 2016-06-21 17:56:00<br>num.completed.cum: 835","EndDate: 2016-06-28 21:32:44<br>num.completed.cum: 836","EndDate: 2016-06-28 22:12:14<br>num.completed.cum: 837","EndDate: 2016-06-29 03:48:10<br>num.completed.cum: 838","EndDate: 2016-06-29 04:40:50<br>num.completed.cum: 839","EndDate: 2016-06-29 06:47:09<br>num.completed.cum: 840","EndDate: 2016-06-29 13:42:15<br>num.completed.cum: 841","EndDate: 2016-07-01 11:58:53<br>num.completed.cum: 842","EndDate: 2016-07-05 00:39:14<br>num.completed.cum: 843"],"key":null,"type":"scatter","mode":"lines","name":"","line":{"width":1.88976377952756,"color":"rgba(127,127,127,1)","dash":"solid","shape":"hv"},"showlegend":false,"xaxis":"x","yaxis":"y","hoverinfo":"text"},{"x":[1461196800,1461196800,null,1461283200,1461283200,null,1461369600,1461369600,null,1461888000,1461888000,null,1461974400,1461974400,null,1462233600,1462233600,null,1465344000,1465344000],"y":[-41.1,885.1,null,-41.1,885.1,null,-41.1,885.1,null,-41.1,885.1,null,-41.1,885.1,null,-41.1,885.1,null,-41.1,885.1],"text":["as.numeric(email_day): 1461196800<br>email_type: Invitation  <br>Groups 1-3","as.numeric(email_day): 1461196800<br>email_type: Invitation  <br>Groups 1-3","as.numeric(email_day): 1461196800<br>email_type: Invitation  <br>Groups 1-3","as.numeric(email_day): 1461283200<br>email_type: Invitation  <br>Groups 4-6","as.numeric(email_day): 1461283200<br>email_type: Invitation  <br>Groups 4-6","as.numeric(email_day): 1461283200<br>email_type: Invitation  <br>Groups 4-6","as.numeric(email_day): 1461369600<br>email_type: Invitation  <br>Groups 7-8","as.numeric(email_day): 1461369600<br>email_type: Invitation  <br>Groups 7-8","as.numeric(email_day): 1461369600<br>email_type: Invitation  <br>Groups 7-8","as.numeric(email_day): 1461888000<br>email_type: Invitation  <br>Groups 10-13","as.numeric(email_day): 1461888000<br>email_type: Invitation  <br>Groups 10-13","as.numeric(email_day): 1461888000<br>email_type: Invitation  <br>Groups 10-13","as.numeric(email_day): 1461974400<br>email_type: Invitation  <br>Groups 14-15","as.numeric(email_day): 1461974400<br>email_type: Invitation  <br>Groups 14-15","as.numeric(email_day): 1461974400<br>email_type: Invitation  <br>Groups 14-15","as.numeric(email_day): 1462233600<br>email_type: Invitation  <br>Groups 16-28","as.numeric(email_day): 1462233600<br>email_type: Invitation  <br>Groups 16-28","as.numeric(email_day): 1462233600<br>email_type: Invitation  <br>Groups 16-28","as.numeric(email_day): 1465344000<br>email_type: Invitation  <br>Group 9","as.numeric(email_day): 1465344000<br>email_type: Invitation  <br>Group 9"],"key":null,"type":"scatter","mode":"lines","name":"Invitation  ","line":{"width":1.88976377952756,"color":"rgba(248,118,109,1)","dash":"solid"},"legendgroup":"Invitation  ","showlegend":true,"xaxis":"x","yaxis":"y","hoverinfo":"text"},{"x":[1462320000,1462320000,null,1462924800,1462924800],"y":[-41.1,885.1,null,-41.1,885.1],"text":["as.numeric(email_day): 1462320000<br>email_type: Reminder  <br>Groups 1-8","as.numeric(email_day): 1462320000<br>email_type: Reminder  <br>Groups 1-8","as.numeric(email_day): 1462320000<br>email_type: Reminder  <br>Groups 1-8","as.numeric(email_day): 1462924800<br>email_type: Reminder  <br>Groups 10-28","as.numeric(email_day): 1462924800<br>email_type: Reminder  <br>Groups 10-28"],"key":null,"type":"scatter","mode":"lines","name":"Reminder  ","line":{"width":1.88976377952756,"color":"rgba(0,186,56,1)","dash":"solid"},"legendgroup":"Reminder  ","showlegend":true,"xaxis":"x","yaxis":"y","hoverinfo":"text"},{"x":[1465257600,1465257600,null,1465344000,1465344000,null,1467158400,1467158400],"y":[-41.1,885.1,null,-41.1,885.1,null,-41.1,885.1],"text":["as.numeric(email_day): 1465257600<br>email_type: Final reminder<br>Groups 10-28","as.numeric(email_day): 1465257600<br>email_type: Final reminder<br>Groups 10-28","as.numeric(email_day): 1465257600<br>email_type: Final reminder<br>Groups 10-28","as.numeric(email_day): 1465344000<br>email_type: Final reminder<br>Groups 1-8","as.numeric(email_day): 1465344000<br>email_type: Final reminder<br>Groups 1-8","as.numeric(email_day): 1465344000<br>email_type: Final reminder<br>Groups 1-8","as.numeric(email_day): 1467158400<br>email_type: Final reminder<br>Group 9","as.numeric(email_day): 1467158400<br>email_type: Final reminder<br>Group 9"],"key":null,"type":"scatter","mode":"lines","name":"Final reminder","line":{"width":1.88976377952756,"color":"rgba(97,156,255,1)","dash":"solid"},"legendgroup":"Final reminder","showlegend":true,"xaxis":"x","yaxis":"y","hoverinfo":"text"}],"layout":{"margin":{"b":27.8953922789539,"l":47.0236612702366,"t":27.1581569115816,"r":7.97011207970112},"plot_bgcolor":"rgba(255,255,255,1)","paper_bgcolor":"rgba(255,255,255,1)","font":{"color":"rgba(0,0,0,1)","family":"","size":15.9402241594022},"xaxis":{"type":"linear","autorange":false,"tickmode":"array","range":[1460846836.85,1468019588.15],"ticktext":["April 18","April 25","May  2","May  9","May 16","May 23","May 30","June  6","June 13","June 20","June 27","July  4"],"tickvals":[1460937600,1461542400,1462147200,1462752000,1463356800,1463961600,1464566400,1465171200,1465776000,1466380800,1466985600,1467590400],"ticks":"outside","tickcolor":"rgba(179,179,179,1)","ticklen":3.98505603985056,"tickwidth":0.33208800332088,"showticklabels":true,"tickfont":{"color":"rgba(77,77,77,1)","family":"","size":12.7521793275218},"tickangle":-0,"showline":false,"linecolor":null,"linewidth":0,"showgrid":true,"domain":[0,1],"gridcolor":"rgba(217,217,217,1)","gridwidth":0.33208800332088,"zeroline":false,"anchor":"y","title":"","titlefont":{"color":"rgba(0,0,0,1)","family":"","size":15.9402241594022},"hoverformat":".2f"},"yaxis":{"type":"linear","autorange":false,"tickmode":"array","range":[-41.1,885.1],"ticktext":["0","200","400","600","800"],"tickvals":[0,200,400,600,800],"ticks":"outside","tickcolor":"rgba(179,179,179,1)","ticklen":3.98505603985056,"tickwidth":0.33208800332088,"showticklabels":true,"tickfont":{"color":"rgba(77,77,77,1)","family":"","size":12.7521793275218},"tickangle":-0,"showline":false,"linecolor":null,"linewidth":0,"showgrid":true,"domain":[0,1],"gridcolor":"rgba(217,217,217,1)","gridwidth":0.33208800332088,"zeroline":false,"anchor":"x","title":"Cumulative number of responses","titlefont":{"color":"rgba(0,0,0,1)","family":"","size":15.9402241594022},"hoverformat":".2f"},"shapes":[{"type":"rect","fillcolor":"transparent","line":{"color":"rgba(179,179,179,1)","width":0.66417600664176,"linetype":"solid"},"yref":"paper","xref":"paper","x0":0,"x1":1,"y0":0,"y1":1}],"showlegend":true,"legend":{"bgcolor":"rgba(255,255,255,1)","bordercolor":"transparent","borderwidth":1.88976377952756,"font":{"color":"rgba(0,0,0,1)","family":"","size":12.7521793275218},"y":1},"hovermode":"closest"},"source":"A","config":{"modeBarButtonsToRemove":["sendDataToCloud"]},"base_url":"https://plot.ly"},"evals":[],"jsHooks":[]}</script><!--/html_preserve-->

# References

