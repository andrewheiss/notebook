Title: Survey technical details
Date: 2016-04-21
Modified: 2016-04-25 21:17:02
Tags: survey
Slug: survey-technical-details

Sending out invitations to ≈30,000 e-mail addresses—many of which are dead and defunct—is tricky. That's a high volume of e-mail and having too many bounces runs the risk of blacklisting my domain.

I used a combination of a custom domain + SendGrid + Zoho + fancy branding + Litmus to send out a lot of e-mail, maintain a good sending reputation, and hopefully boost response rates.

Here's what I did.


# Custom domain

I debated whether to send all the e-mails using my .edu e-mail address or something else. Using the .edu address has a built-in psychological benefit—messages probably look more legitimate and research based than blah@gmail.com. However, sending out such a high volume of e-mail from Duke's server is hard/impossible, as I discovered when running a survey of human trafficking NGOs in 2013. I also didn't want to flood my inbox with bounce notifications and survey responses.

Rather than make a Gmail account, which doesn't look as professional, I purchased the [ingoresearch.org](https://www.ingoresearch.org/) domain and created a survey@ingoresearch.org account. It used to be possible to use Google Apps for e-mail on custom domains, but they stopped offering that service in 2012. Instead, I used [Zoho](https://www.zoho.com/), which offers similar services.

- [Generic DNS settings for MX records](https://www.zoho.com/mail/help/adminconsole/configure-email-delivery.html)
- [SPF record](https://www.zoho.com/mail/help/adminconsole/spf-configuration.html)
- [DomainKey/DKIM public key](https://www.zoho.com/mail/help/adminconsole/domain-keys-configuration.html)


# SendGrid

I ran the human trafficking NGO survey using Excel (for tracking e-mails and responses), Word (for mail merge), and Outlook (for sending mail through my adviser's account). That survey only went out to ≈1,500 NGOs, and it was a technical nightmare.

So I did what all the cool kids do and used an e-mail delivery service. [GitHub's educational pack](https://education.github.com/pack) included a free student plan for [SendGrid](https://sendgrid.com/), so I made an account there and played around with it.

SendGrid is awesome.

Their API is powerful and lets you send lots of e-mail quickly. The [Python wrapper for the API](https://github.com/sendgrid/sendgrid-python) is easy to use and intuitive ([see?](https://github.com/andrewheiss/Dissertation/blob/master/Data/Survey/send_mail.py)). They have a nice templating engine and analytic and tracking features. Note to self: use SendGrid for all future survey administration.

To boost its reputation, I [whitelabeled](https://sendgrid.com/docs/User_Guide/Settings/Whitelabel/index.html) the ingoresearch.org domain and all outgoing links. Despite all this DNS whitelabeling, my reputation took a huge hit after the first round of 2,000 e-mails, likely because there were so many bounces (i.e. it dropped from 100% to 76% (!)). I also enabled [List-Unsubscribe](https://support.sendgrid.com/hc/en-us/articles/204379093-How-do-I-add-a-list-unsubscribe-header-to-my-emails-) in the SendGrid settings.

After sending ≈8,000 e-mails, my [SendGrid reputation](https://sendgrid.com/docs/Classroom/Deliver/Address_Lists/list_scrubbing_guide.html) dropped below 75% and my account was suspended. I'm working with them right now to get the account restored and get back to e-mailing. Right before this happened (spurred on by fears that something like this would happen), I caved and spent $100 to clean and scrub my list of e-mails using [Email Hippo](https://www.emailhippo.com/en-US). Roughly 30% of the e-mail addresses I submitted were dead and would have bounced, so now I have a smaller and cleaner list of addresses, which should help with my SendGrid reputation

[MailTester.com](https://www.mail-tester.com) is incredibly useful for checking for issues with e-mails. For instance, it found that my e-mails were incredibly heavy, since the HTML template was heavily commented. I minified the CSS to resolve that issue.

All survey invitations come from survey@ingoresearch.org and all bounces are forwarded to bounces@ingoresearch.org.

I [randomly assigned each e-mail address](https://github.com/andrewheiss/Dissertation/blob/master/Data/Survey/master_ingo_list.R) to a group of roughly 1,000 organizations and ran the sending script on each group.

# Branding

Finally, based on previous research and experiences in big online surveys [@Buthe:2011; @EdwardsRobertsClarke:2009; @HeissKelley:2016], I created a simple unified brand for the survey (mostly just a logo and color scheme.)

I used two Creative Commons-licensed images from The Noun Project ([World, by Shmidt Sergey](https://thenounproject.com/term/world/149710/); and [World, by Dalpat Prajapati](https://thenounproject.com/term/world/64588/)). The UN has a set of unified visual icons in the public domain, but [the one for NGOs is kind of uninspiring](https://thenounproject.com/term/ngo-office/4403/).

## Fonts

- [Source Sans Pro](https://github.com/adobe-fonts/source-sans-pro) Light, Semibold, and Black

## Colors

- <span style="padding: 0.2em; background-color: #00529b; color: #ffffff;">Blue</span>: `#00529b`
- <span style="padding: 0.2em; background-color: #FF6719; color: #ffffff;">Orange</span>: `#FF6719`

## Full logo

![](/files/images/ingo-survey-logo-big.png){.pure-img-responsive}

## Small logo

![](/files/images/ingo-survey-logo.png){.pure-img-responsive}


## E-mail template

[HTML e-mail templates](http://webdesign.tutsplus.com/tutorials/what-you-should-know-about-html-email--webdesign-12908) are a [massive pain](http://genius.com/7982100). I used [Litmus](https://litmus.com/) to (1) adapt a pre-built template styled off of MailChimp's default template and (2) preview it in different e-mail programs. I discovered [Foundation for Emails](http://foundation.zurb.com/emails.html) after I had already made and tested the template—next time I do this, I'll use their templating system first.

[View all the e-mail invitations.](/project/diss-ingos-in-autocracies/survey-invitations/)

![](/files/images/ingo-survey-email.png){.pure-img-responsive}


# References
