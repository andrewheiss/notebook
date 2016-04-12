Title: Annotated survey draft
Date: 2016-04-12
Modified: 2016-04-12
Class: survey
Slug: survey-draft

# Consent

You have been invited to participate in a research survey about the relationship between international nongovernmental organizations (INGOs) and the governments of their host countries. This survey is part of a study by Andrew Heiss from Duke University in the United States, with oversight by his adviser, Dr. Judith Kelley.

Your participation is entirely voluntary and you are free to skip any question or withdraw from the survey at any time. The survey should take about 10 minutes to complete. *Please answer in whatever language you feel most comfortable using*.

Results from the survey will be used in aggregate so that it will not be possible to identify any individual organization. You can also explicitly choose to remain anonymous. Your responses will be securely transmitted to Qualtrics.com and stored in a password protected electronic format. The information you provide will be analyzed with statistical software and used in academic research.

You will receive no direct benefits from participating in this research study, but your responses may reveal important and useful insights in how INGOs relate to their host governments, which can benefit other similar organizations.

If you have any questions at any time about the study or the procedures, you can contact Andrew Heiss at andrew.heiss@duke.edu or +1 801-734-9327. You can also contact Dr. Judith Kelley at judith.kelley@duke.edu or +1 919-613-7343.

I have read the above information, and I consent to take part in the study.

:    Single answer

    - Yes
    - No

---

# Introductory questions

*Q1.1* What is the name of your organization?

:   Text field

*Q1.2* Where is your organization's headquarters?

:   Autocomplete text field populated with a list of countries

    [How to add this to Qualtrics](/project/diss-ingos-in-autocracies/survey-notes/)

*Q1.3* What is your position in the organization?

:    Single answer

    - Executive director
    - Program officer
    - Public relations officer 
    - Staff member
    - Receptionist
    - Other

*Q1.4* Does your organization work in a country other than your home country?

:   If the respondent answers no, end the survey early since they're not an INGO

    Single answer

    - Yes
    - No


*Q1.5* In how many countries does your organization work?

:   Numeric text field

---

# Organizational questions

*Q2.1* Which issues does your organization focus on?

:   Multiple answers allowed

    Option order randomized (except "Other", which stays at the bottom)

    - Development
    - Human rights
    - Environment
    - Education
    - Disaster relief
    - Freedom of expression
    - Democracy assistance
    - Human trafficking
    - Other

*Q2.2* Which issue does your organization focus on *the most*?

:   Text field

---

*Q2.3* Please indicate how often your organization engages in each of these types of activities:

:   Qualtrics side-by-side table

    |                                                                                             | Always | Most of the time | About half the time | Sometimes | Never | Don't know | Not applicable |
    |---------------------------------------------------------------------------------------------|:------:|:----------------:|:-------------------:|:---------:|:-----:|:----------:|:--------------:|
    | Providing direct aid and services                                                           |    •   |         •        |          •          |     •     |   •   |      •     |        •       |
    | Engaging in research and public education                                                   |    •   |         •        |          •          |     •     |   •   |      •     |        •       |
    | Mobilizing people (e.g. campaigns, public protests)                                         |    •   |         •        |          •          |     •     |   •   |      •     |        •       |
    | Engaging in advocacy                                                                        |    •   |         •        |          •          |     •     |   •   |      •     |        •       |
    | Monitoring and assessing the effects of policies, international agreements, and commitments |    •   |         •        |          •          |     •     |   •   |      •     |        •       |

---

*Q2.4* How does your organization provide direct aid and services?

:   Multiline text field

    Display if Q2.3's "Providing direct aid and services" is "Sometimes" or greater

*Q2.5* How does your organization engage in research and public education?

:   Multiline text field

    Display if Q2.3's "Engaging in research and public education" is "Sometimes" or greater

*Q2.6* How does your organization mobilize people?

:   Multiline text field

    Display if Q2.3's "Mobilizing people" is "Sometimes" or greater

*Q2.7* How does your organization engage in advocacy?

:   Multiline text field

    Display if Q2.3's "Engaging in advocacy" is "Sometimes" or greater

*Q2.8* How does your organization monitor and assess policies, agreements, and commitments?

:   Multiline text field

    Display if Q2.3's "Monitoring and assessing…" is "Sometimes" or greater

---

*Q2.9* Approximately how many full-time employees does your organization have?

:   Numeric text field

*Q2.10* Approximately how many volunteers does your organization have?

:   Numeric text field

*Q2.11* How would you describe your organization's structure?

:   Single answer

    - A unitary independent organization
    - A subsidiary of a larger organization
    - A coalition or federation of independent organizations
    - Other
    - Don't know

*Q2.12* Does your organization collaborate with other organizations or institutions?

:   Multiple answers allowed

    - Other nongovernmental organizations (NGOs)
    - International organizations (IGOs)
    - Governments
    - Corporations or businesses
    - Other
    - Don't know
    - We do not collaborate with other organizations

*Q2.13* Please list a few of the organizations you partner with most often:

:   Text field

    Display if Q2.12 is not "Don't know" or "We do not…"

*Q2.14* How much of your organization's funding comes from each of these sources?

:   Qualtrics side-by-side table

    |                      | A great deal | A lot | A moderate amount | A little | None at all | Don't know | Not applicable |
    |----------------------|:------------:|:-----:|:-----------------:|:--------:|:-----------:|:----------:|:--------------:|
    | Individual donations |       •      |   •   |         •         |     •    |      •      |      •     |        •       |
    | Corporate donations  |       •      |   •   |         •         |     •    |      •      |      •     |        •       |
    | Foundation donations |       •      |   •   |         •         |     •    |      •      |      •     |        •       |
    | Government grants    |       •      |   •   |         •         |     •    |      •      |      •     |        •       |
    | Other                |       •      |   •   |         •         |     •    |      •      |      •     |        •       |

**Q2.15** Question about how they measure and evaluate programs

:   For Bush:2015 taming

    `TODO`

---

*Q2.16* In general, what would you say your organization is trying to accomplish?

:   Multiline text field

*Q2.17* How is your organization's mission, vision, and values reflected in these objectives?

:   Multiline text field

*Q2.18* Have these objectives changed any in the last 10 years? If so, how?

:   Multiline text field

*Q2.19* What are the major obstacles, if any, to reaching your organization's objectives?

:   Multiline text field

*Q2.20* Are there any changes that you would like to see in your organization's goals and strategies, now or in the future?

:   Multiline text field

---

# Government relations

## General questions

*Q3.1* Other than your organization's headquarters country, where does your organization work the most? *Or where has the organization been most restricted?*

:   Autocomplete text field populated with a list of countries

    Validate that it's not the same as their home country

*Q3.2* How long has your organization worked in `country_name`?

:   Single answer

    - Less than 1 year
    - 1–4 years
    - 5–9 years
    - 10 years or more
    - Don't know

*Q3.3* What does your organization do in `country_name`?

:   Multiple answers allowed

    - Maintain a physical office staffed primarily by foreigners
    - Maintain a physical office staffed primarily by people from `country_name`
    - Provide funding to domestic NGOs
    - Partner with domestic NGOs
    - Don't know

*Q3.4* Is your organization registered with the national government in `country_name`?

:   Single answer

    - Yes
    - No
    - Don't know

---

## Contact with government

*Q3.5* About how often does your organization have contact with government or party officials in `country_name`?

:   Single answer

    - Once a week
    - Once a month
    - Once a year
    - Once every 2+ years
    - Never
    - Don't know

*Q3.6* What kind of government officials does your organization have contact with?

:   Multiple answers allowed

    - President or prime minister
    - Member of parliament
    - Head of a ministry
    - Ministry staff
    - Military
    - Police or internal security
    - We have no contact with government officials
    - Don't know

*Q3.7* What kind of government officials does your organization have contact with *most often*?

:   Text field

*Q3.8* How often is your organization required to report to the government of `country_name`?

:   Single answer

    - Once a week
    - Once a month
    - Once a year
    - Once every few years
    - Never
    - Don't know

*Q3.9* Are members of the government or ruling party of `country_name` involved in your work?

:   Single answer

    - Yes
    - No
    - Don't know

*Q3.10* How is the government of `country_name` involved in your work?

:   Multiline text field

---

## Relationship with government

*Q3.11* How would you characterize your organization's relationship with the government of `country_name`? *Please note all survey responses will be kept strictly confidential*.

:   Single answer

    - Extremely negative
    - Somewhat negative
    - Neither positive nor negative
    - Somewhat positive
    - Extremely positive
    - Don't know
    - Prefer not to answer

*Q3.12* Briefly describe your organization's relationship with the government of `country_name`:

:   Multiline text field

---

## NGO regulations and restrictions

*Q3.13* How familiar is your organization with regulations for international nongovernmental organizations (NGOs) in `country_name`?

:   Single answer

    - Extremely familiar
    - Very familiar
    - Moderately familiar
    - Slightly familiar
    - Not familiar at all
    - Don't know

*Q3.14* How often do regulations for NGOs in `country_name` change?

:   Single answer

    - Once a month
    - Once a year
    - Once every few years
    - Rarely
    - Never
    - Don't know

*Q3.15* How does your organization find out about changes to NGO regulations in `country_name`?

:   Multiple answers allowed

    - Government officials
    - Other NGOs
    - Newspapers, television, and other media
    - The internet
    - Other
    - Don't know

---

*Q3.16* How is your organization affected by the following types of legal barriers for international NGOs in `country_name`?

:   Qualtrics side-by-side table

    Types of legal barriers adapted from the [2012 Defending Civil Society Report](http://www.defendingcivilsociety.org/dl/reports/DCS_Report_Second_Edition_English.pdf)

    |                                           | A great deal | A lot | A moderate amount | A little | Not at all | Don't know | Not applicable |  Comments  |
    |-------------------------------------------|:------------:|:-----:|:-----------------:|:--------:|:----------:|:----------:|:--------------:|:----------:|
    | Barriers to entry                         |       •      |   •   |         •         |     •    |      •     |      •     |        •       | Text field |
    | Barriers to operational activity          |       •      |   •   |         •         |     •    |      •     |      •     |        •       | Text field |
    | Barriers to speech and advocacy           |       •      |   •   |         •         |     •    |      •     |      •     |        •       | Text field |
    | Barriers to communication and cooperation |       •      |   •   |         •         |     •    |      •     |      •     |        •       | Text field |
    | Barriers to assembly                      |       •      |   •   |         •         |     •    |      •     |      •     |        •       | Text field |
    | Barriers to resources                     |       •      |   •   |         •         |     •    |      •     |      •     |        •       | Text field |

---

*Q3.17* Overall, how much is your organization's work restricted by the government of `country_name`?

:   Single answer

    - Extremely restricted
    - Very restricted
    - Moderately restricted
    - Slightly restricted
    - Not restricted at all
    - Don't know

*Q3.18* How do the local laws and regulations in `country_name` affect your organization's ability to pursue its mission?

:   Multiline text field

---

## Responses to regulations

*Q3.19* Has your organization changed its typical strategy because of government regulations in `country_name`?

:   Single answer

    - Yes
    - No
    - Don't know

*Q3.20* How has your organization changed its typical strategy in `country_name`?

:   Multiline text field

*Q3.21* Has your organization discussed NGO regulations with government officials in `country_name`?

:   Single answer

    - Yes
    - No
    - Don't know

*Q3.22* Has your organization tried to change NGO regulations in `country_name`?

:   Single answer

    - Yes
    - No
    - Don't know

---

# Final questions

*Q4.1* What challenges does your organization face when working in democratic countries?

:   Multiline text field

*Q4.2* What challenges does your organization face when working in less democratic (i.e. authoritarian) countries?

:   Multiline text field

---

*Q4.3* Do you have any final comments?

:   Multiline text field

---

*Q4.4* May I contact you for any follow up questions?

:   Single answer

    - Yes
    - No

*Q4.5* Would you like to be notified of the results of this survey once it is completed?

:   Single answer

    - Yes
    - No

*Q4.6* Please provide an e-mail address I can use to contact you:

:   Text field

---

Thank you for participating in this research.

If you have any questions or concerns about this survey, please feel free to contact Andrew Heiss by e-mail at andrew.heiss@duke.edu or by phone at +1 801-734-9327
