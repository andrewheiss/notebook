Title: Annotated survey
Date: 2016-04-12
Modified: 2016-04-19 16:51:58
Class: survey
Slug: ingo-survey-annotated

# Consent

*Q1.1*: You have been invited to participate in a research survey about the relationship between international nongovernmental organizations (INGOs) and the governments of their host countries. This survey is part of a study by Andrew Heiss from Duke University in the United States, with oversight by his adviser, Dr. Judith Kelley.

Your participation is entirely voluntary and you are free to skip any question or withdraw from the survey at any time. The survey should take about **15 minutes** to complete. ***Please answer in whatever language you feel most comfortable using***.

Results from the survey will be used in aggregate so that it will not be possible to identify any individual organization. You can also explicitly choose to remain anonymous. Your responses will be securely transmitted to Qualtrics.com and stored in a password protected electronic format. The information you provide will be analyzed with statistical software and used in academic research.

You will receive no direct benefits from participating in this research study, but your responses may reveal important and useful insights in how INGOs relate to their host governments, which can benefit other similar organizations.

If you have any questions at any time about the study or the procedures, you can contact Andrew Heiss at andrew.heiss@duke.edu or +1 801-734-9327. You can also contact Dr. Judith Kelley at judith.kelley@duke.edu or +1 919-613-7343.

**I have read the above information, and I consent to take part in the study.**

:    Single answer

    - Yes
    - No

    If the respondent doesn't consent, skip to Q6.1 and end the survey

---

# Introductory questions

*Q2.1*: What is the name of your organization?

:   Text field

*Q2.2*: Where is your organization's headquarters?

:   Dropdown menu with [country names from the World Bank](/project/diss-ingos-in-autocracies/survey-countries/).

    Though dropdown menus are poor UI, [adding an autocomplete field to Qualtrics is doable](/project/diss-ingos-in-autocracies/survey-notes/), but tricky and won't always work consistently (e.g. if a respondent disables JavaScript, validating their response nearly impossible since they'll have to type the name of the country in blindly—and perfectly—to make it match the validating regex).

*Q2.3*: What is your position in your organization?

:    Single answer

    - Executive director
    - Program officer
    - Public relations officer
    - Staff member
    - Receptionist
    - Other:

---

*Q2.4*: Does your organization work in a country other than `home_country`?

:   If the respondent answers no, skip to Q7.1 and end the survey early since they're not an INGO

    Single answer

    - Yes
    - No

*Q2.5*: Besides `home_country`, where does your organization work?

:   Checkboxes with multiple answers allowed; each country is an option

    Horrible nasty UX here, but ¯\\\_(ツ)\_/¯. There's no good way to do this in Qualtrics


---

# Organizational questions

*Q3.1*: Which issues does your organization focus on? (select all that apply)

:   Multiple answers allowed

    - Development
    - Human rights
    - Environment
    - Education
    - Disaster relief
    - Freedom of expression
    - Democracy assistance
    - Human trafficking
    - Other:

*Q3.2*: Which issue does your organization focus on *the most*? (select one)

:   Single answer

    - Development
    - Human rights
    - Environment
    - Education
    - Disaster relief
    - Freedom of expression
    - Democracy assistance
    - Human trafficking
    - Other:

---

*Q3.3*: Please indicate how often your organization engages in each of these types of activities:

:   Qualtrics side-by-side table

    |                                                                                             | Always | Most of the time | About half the time | Sometimes | Never | Don't know | Not applicable | Please explain briefly |
    |---------------------------------------------------------------------------------------------|:------:|:----------------:|:-------------------:|:---------:|:-----:|:----------:|:--------------:|:----------------------:|
    | Providing direct aid and services                                                           |    •   |         •        |          •          |     •     |   •   |      •     |        •       |       Text field       |
    | Engaging in research and public education                                                   |    •   |         •        |          •          |     •     |   •   |      •     |        •       |       Text field       |
    | Mobilizing people (e.g. campaigns, public protests)                                         |    •   |         •        |          •          |     •     |   •   |      •     |        •       |       Text field       |
    | Engaging in advocacy                                                                        |    •   |         •        |          •          |     •     |   •   |      •     |        •       |       Text field       |
    | Monitoring and assessing the effects of policies, international agreements, and commitments |    •   |         •        |          •          |     •     |   •   |      •     |        •       |       Text field       |

---

*Q3.4*: Approximately how many full-time employees does your organization have?

:   Numeric text field

*Q3.5*: Approximately how many volunteers does your organization have?

:   Numeric text field

*Q3.6*: Does your organization collaborate with any of these organizations or institutions? (select all that apply)

:   Multiple answers allowed

    - Other nongovernmental organizations (NGOs)
    - International organizations (IGOs)
    - Governments
    - Corporations or businesses
    - Other:
    - Don't know
    - We do not collaborate with other organizations or institutions

*Q3.7*: Please list a few of the organizations or institutions you partner with most often:

:   Text field

*Q3.8*: How much of your organization's funding comes from each of these sources?

:   Qualtrics side-by-side table

    |                                                                                       | A great deal | A lot | A moderate amount | A little | None at all | Don't know | Not applicable |
    | ------------------------------------------------------------------------------------- | :----------: | :---: | :---------------: | :------: | :---------: | :--------: | :------------: |
    | Individual donations                                                                  |      •       |   •   |         •         |    •     |      •      |     •      |       •        |
    | Corporate donations                                                                   |      •       |   •   |         •         |    •     |      •      |     •      |       •        |
    | Foundation donations                                                                  |      •       |   •   |         •         |    •     |      •      |     •      |       •        |
    | Grants from the government of the country in which your organization is headquartered |      •       |   •   |         •         |    •     |      •      |     •      |       •        |
    | Grants from the government of the country in which your organization works            |      •       |   •   |         •         |    •     |      •      |     •      |       •        |
    | Other                                                                                 |      •       |   •   |         •         |    •     |      •      |     •      |       •        |

---

*Q3.9*: In general, what would you say your organization is trying to accomplish?

:   Multiline text field

*Q3.10*: How is your organization's mission, vision, and values reflected in these objectives?

:   Multiline text field

*Q3.11*: Have these objectives changed at all in the last 10 years? If so, how?

:   Multiline text field

*Q3.12*: What are the major obstacles, if any, to reaching your organization's objectives?

:   Multiline text field

*Q3.13*: Are there any changes that you would like to see in your organization's goals and strategies, now or in the future?

:   Multiline text field


---

# Government relations

Enable "Loop and merge" for this block. Respondents can fill out this section as many times as they want for each of the countries they work in.

[Qualtrics' solution for complicated looping and merging is pretty kludgy](https://support.qualtrics.com/survey-platform/edit-survey/block-options/loop-and-merge#LoopingBasedOnAYesNo). Respondents can repeat this block up to 5 times (regardless of how many countries they work in). The final question of this block, Q4.24, lets respondents either restart the block or continue to the next block.

In order to end the cycle of loops early, **each question in this block** needs to have display logic hiding itself if the respondent chooses to end the loop:

![Display logic for every question in the looped block](/files/images/survey-loop-display-logic.png){.pure-img-responsive}

It's a mess, but it works.


## General questions

*Q4.1*: I will now ask a series of questions about your organization's relationship to the government of one of the countries you work in. Please select a country you would like to discuss:

:   Single answer

    Options populated from the countries selected in Q2.5

*Q4.2*: How long has your organization worked in `target_country`?

:   Single answer

    - Less than 1 year
    - 1–4 years
    - 5–9 years
    - 10 years or more
    - Don't know

*Q4.3*: What does your organization do in `target_country`? (select all that apply)

:   Multiple answers allowed

    - Maintain a physical office staffed primarily by foreigners
    - Maintain a physical office staffed primarily by people from `target_country`
    - Provide funding to domestic NGOs
    - Partner with domestic NGOs
    - Don't know

*Q4.4*: Is your organization registered with the national government in `target_country`?

:   Single answer

    - Yes
    - No
    - Don't know

---

## Contact with government

*Q4.5*: About how often does your organization have contact with government or party officials in `target_country`?

:   Single answer

    - Once a week
    - Once a month
    - Once a year
    - Once every 2+ years
    - Never
    - Don't know
    - Other:

*Q4.6*: What kind of government officials does your organization have contact with? (select all that apply)

:   Multiple answers allowed

    - President or prime minister
    - Member of parliament
    - Head of a ministry
    - Ministry staff
    - Military
    - Police or internal security
    - Other:
    - We have no contact with government officials
    - Don't know

*Q4.7*: What kind of government officials does your organization have contact with *most often*? (select one)

:   Single answer

    - President or prime minister
    - Member of parliament
    - Head of a ministry
    - Ministry staff
    - Military
    - Police or internal security
    - Other:
    - We have no contact with government officials
    - Don't know

*Q4.8*: How often is your organization required to report to the government of `target_country`?

:   Single answer

    - Once a week
    - Once a month
    - Once a year
    - Once every few years
    - Never
    - Don't know
    - Other:

*Q4.9*: Are members of the government or ruling party of `target_country` involved in your work?

:   Single answer

    - Yes
    - No
    - Don't know

*Q4.10*: How is the government of `target_country` involved in your work?

:   Multiline text field

---

## Relationship with government

*Q4.11*: How would you characterize your organization's relationship with the government of `target_country`? *Please note all survey responses will be kept strictly confidential*.

:   Single answer

    - Extremely negative
    - Somewhat negative
    - Neither positive nor negative
    - Somewhat positive
    - Extremely positive
    - Don't know
    - Prefer not to answer

*Q4.12*: Briefly describe your organization's relationship with the government of `target_country`:

:   Multiline text field

---

## NGO regulations and restrictions

*Q4.13*: How familiar is your organization with regulations for international nongovernmental organizations (NGOs) in `target_country`?

:   Single answer

    - Extremely familiar
    - Very familiar
    - Moderately familiar
    - Slightly familiar
    - Not familiar at all
    - Don't know

*Q4.14*: How often do regulations for international NGOs in `target_country` change?

:   Single answer

    - Once a month
    - Once a year
    - Once every few years
    - Rarely
    - Never
    - Don't know

*Q4.15*: How does your organization find out about changes to NGO regulations in `target_country`? (select all that apply)

:   Multiple answers allowed

    - Government officials
    - Other NGOs
    - Newspapers, television, and other media
    - The internet
    - Other:
    - Don't know

---

*Q4.16*: How is your organization affected by the following types of legal regulations for international NGOs in `target_country`?

:   Qualtrics side-by-side table

    Types of legal barriers adapted from the [2012 Defending Civil Society Report](http://www.defendingcivilsociety.org/dl/reports/DCS_Report_Second_Edition_English.pdf)

    |                                                     | A great deal | A lot | A moderate amount | A little | Not at all | Don't know | Not applicable | Please explain briefly |
    | --------------------------------------------------- | :----------: | :---: | :---------------: | :------: | :--------: | :--------: | :------------: | :--------------------: |
    | Regulations regarding registration                  |      •       |   •   |         •         |    •     |     •      |     •      |       •        |       Text field       |
    | Regulations regarding operations                    |      •       |   •   |         •         |    •     |     •      |     •      |       •        |       Text field       |
    | Regulations regarding speech and advocacy           |      •       |   •   |         •         |    •     |     •      |     •      |       •        |       Text field       |
    | Regulations regarding communication and cooperation |      •       |   •   |         •         |    •     |     •      |     •      |       •        |       Text field       |
    | Regulations regarding assembly                      |      •       |   •   |         •         |    •     |     •      |     •      |       •        |       Text field       |
    | Regulations regarding resources                     |      •       |   •   |         •         |    •     |     •      |     •      |       •        |       Text field       |

---

*Q4.17*: Overall, how is your organization's work affected by government regulations in `target_country`?

:   Single answer

    - Not restricted at all
    - Slightly restricted
    - Moderately restricted
    - Very restricted
    - Extremely restricted
    - Don't know

*Q4.18*: How do the local laws and regulations in `target_country` affect your organization's ability to pursue its mission?

:   Multiline text field

---

## Responses to regulations

*Q4.19*: Over the last 10 years, has your organization changed its mix of programming in `target_country`?

:   Single answer

    - Yes
    - No
    - Don't know

*Q4.20*: How has your organization's mix of programming changed in `target_country`?

:   Multiline text field

    Display if Q4.19 is "Yes"

*Q4.21*: Has your organization done any of the following in response to changes in government regulations in `target_country`?

:   Qualtrics side-by-side table

    |                                                   | Yes |  No | Don’t know | Not applicable | Please explain briefly |
    | ------------------------------------------------- | :-: | :-: | :--------: | :------------: | :--------------------: |
    | We changed the sources of our funding             |  •  |  •  |     •      |       •        |       Text field       |
    | We changed which issues we work on                |  •  |  •  |     •      |       •        |       Text field       |
    | We changed how we communicate with the government |  •  |  •  |     •      |       •        |       Text field       |
    | We changed how we communicate with our donors     |  •  |  •  |     •      |       •        |       Text field       |
    | We changed which locations we work in             |  •  |  •  |     •      |       •        |       Text field       |
    | We changed the location of our country office     |  •  |  •  |     •      |       •        |       Text field       |
    | We used more local staff and/or volunteers        |  •  |  •  |     •      |       •        |       Text field       |
    | We used more foreign staff and/or volunteers      |  •  |  •  |     •      |       •        |       Text field       |

---

*Q4.22*: Has your organization discussed NGO regulations with government officials in `target_country`?

:   Single answer

    - Yes
    - No
    - Don't know

*Q4.23*: Has your organization tried to change NGO regulations in `target_country`?

:   Single answer

    - Yes
    - No
    - Don't know

---

*Q4.24*: That's all I need to know about your organization's work in `target_country`.  
You can either answer the same set of questions for another country your organization works in (this would be helpful) or move on to the survey's final questions.

:   Single answer

    - Answer questions about another country
    - Continue with survey's final questions


---

# Final questions

*Q5.1*: Do you have any additional comments?

:   Multiline text field

---

*Q5.2*: May I contact you for any follow up questions?

:   Single answer

    - Yes
    - No

*Q5.3*: Would you like to be notified of the results of this survey once it is completed?

:   Single answer

    - Yes
    - No

*Q5.4*: Please provide an e-mail address I can use to contact you:

:   Text field

---

Thank you for participating in this research.

If you have any questions or concerns about this survey, please feel free to contact Andrew Heiss by e-mail at andrew.heiss@duke.edu or by phone at +1 801-734-9327

---

# Optional blocks

## No consent

*Q6.1*: I'm sorry you did not consent to participate in this research. Could you briefly explain why?

:   Multiline text field

## Not INGO

*Q7.1*: This survey is only concerned with international NGOs, or NGOs that work in countries other than the ones they are based in. Based on your responses, your organization only works in `home_country`, indicating that you are not an international NGO.  
If this is a mistake and your organization does work abroad, click here to restart the survey. Otherwise, click on the forward arrow below to end the survey.  
Thanks for your time!

:   Descriptive text
