Title: About this notebook
Date: 2016-04-09
Modified: 2016-04-13 00:48:03
Slug: about

> You can accomplish anything in life, provided that you do not mind who gets the credit.[^1]
> 
> —Harry S. Truman  
> David McCollough, *Truman* (New York: Simon and Schuster, 1992).

> Abandoning the habit of secrecy in favor of process transparency and peer review was the crucial step by which alchemy became chemistry.
> 
> —Eric S. Raymond  
> [*The art of UNIX programming*](https://books.google.com/books?id=H4q1t-jAcBIC&pg=PA440&lpg=PA440&dq=Abandoning+the+habit+of+secrecy+in+favor+of+process+transparency&source=bl&ots=-e4tLoygcr&sig=d4t3wJ-qIDkCxRZxHXYS8iismNk&hl=en&sa=X&ved=0ahUKEwjk0M6OxYrMAhWIKyYKHSsgAUkQ6AEIHTAA#v=onepage&q=Abandoning%20the%20habit%20of%20secrecy%20in%20favor%20of%20process%20transparency&f=false) (Boston: Addison-Wesley, 2003), 440.

# Purpose

Following the example of [Lincoln Mullen](http://notebook.lincolnmullen.com/), [Jason Heppler](http://notebook.jasonheppler.org/), and [Caleb McDaniel](http://wcm1.web.rice.edu/)'s history notebooks, [Carl Boettiger's ecological notebook](http://www.carlboettiger.info/lab-notebook.html), and [Shawn Graham's archeology notebook](https://electricarchaeology.ca/2015/10/06/an-elegant-open-notebook/), this is my own wiki-like space to publicly store all the notes and resources related to my past and ongoing research in public policy, political science, and international relations. Since the beginning of graduate school, I've tried to make my research as open and public as possible, letting other see [how the sausage gets made](http://genius.com/Lin-manuel-miranda-the-room-where-it-happens-lyrics#note-7871352). I regularly post my code and much of my writing on [GitHub](https://github.com/andrewheiss/), but this notebook is my first foray into [open notebook science](https://en.wikipedia.org/wiki/Open_notebook_science), showing the full process of knowledge production. The idea of open notebook science has slowly been spreading among historians and digital humanists, but I haven't seen any political scientists or public policy scholars with one. Perhaps this is the first?

Why an open notebook? Like Caleb McDaniel (who has written [the clearest and logical justification for open notebooks](http://wcm1.web.rice.edu/open-notebook-history.html) I've found), I feel that open research is central to "our scholarly values of open intellectual exchange, integrity, and honesty." With this notebook, "other researchers have access not just to [my] publications, but to the underlying data, methods, and experimental results that drive research projects forward."

This notebook contains notes, primary sources, scribblings, code, figures, half-formed thoughts, and all the other raw materials, by-products, and miscellanea involved in research. I publish more polished essays, tutorials, and code snippets on [my personal blog](https://www.andrewheiss.com/blog/).


# Human and organizational research ethics

One possible reason open notebooks have taken some root among historians, digital humanists, and researchers in the hard sciences is that these disciplines tend to involve dead people and inanimate objects. My own research on international relations, organizational strategies, and other policy issues deals with living people and organizations, and sharing research notes about them can be fraught with privacy and ethical implications.

Thus, this notebook does not contain transcripts from in-person interviews, identifiable survey results, or contact information for people in any organizations I study. When I do link to information related to people, I link to publicly viewable pages such as Twitter profiles or institutional home pages.


# How it works

While [Jekyll](https://jekyllrb.com/) seems to be what all the cool kids use these days for Markdown-based static notebooks or wikis (and it's the foundation for GitHub's own static hosting), and [while I used to use Jekyll](https://github.com/andrewheiss/ah-jekyll) for my own personal site, in 2014 I realized that I only ever used Ruby for one thing—Jekyll. I converted to [Pelican](http://blog.getpelican.com/)—Python's answer to Jekyll—in November 2014 and haven't looked back.

Each note in this notebook is a [plain text file](http://plain-text.co/) written in [pandoc-flavored](http://pandoc.org/) [Markdown](https://daringfireball.net/projects/markdown/). The entire site is stored in a [GitHub repository](https://github.com/andrewheiss/notebook), and you can see all my [fancy/complicated Pelican settings](https://github.com/andrewheiss/notebook/blob/master/pelicanconf.py) there. I use a [Makefile](https://github.com/andrewheiss/notebook/blob/master/Makefile) to build the site locally and upload it to my server with rsync. Maybe someday when I'm a cool kid I'll hook up a [CI service](https://travis-ci.org/) to [build and deploy the site each time I commit to GitHub](http://blog.mathieu-leplatre.info/publish-your-pelican-blog-on-github-pages-via-travis-ci.html). That day is not today.

Because [I block search engines](https://notebook.andrewheiss.com/robots.txt) from this notebook (since the content here is not really meant for final consumption by the public), I use the jQuery-based [Tipue Search](http://www.tipue.com/search/) plugin to search this site.

The morbidly curious can [read about all the software I use](https://www.andrewheiss.com/uses/).

[^1]:   Though you *should* give some credit…
