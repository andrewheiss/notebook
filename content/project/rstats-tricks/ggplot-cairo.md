Title: Using Cairo graphics with ggplot2
Date: 2016-06-20
Modified: 2016-06-20 21:41:40
Slug: ggplot-cairo
Tags: ggplot, cairo, rstats
Highlight: True

Using custom fonts in ggplot graphics is trivial, since pretty much every theme includes a `base_family=` argument. It is more difficult, however, to export these graphics as PDFs with these fonts embedded. R's default PDF plotter has limited support for embedding fonts, and packages that try to address this are just as limited (like [extrafont](https://github.com/wch/extrafont), which only works with True Type Fonts (TTF) and has to load and parse your font library on its first run).

Fortunately, R can use the the [Cairo graphics library](https://cairographics.org/) to embed fonts in PDFs perfectly, regardless of file type, and without the need to load your entire font library. Install the [Cairo package for R](https://cran.r-project.org/web/packages/Cairo/index.html) and use it with either base graphics or with ggplot's `ggsave(..., device=cairo_pdf)`.

The Cairo library can also make better PNGs. Setting a custom DPI with `ggsave()`'s default graphics engine leads to inconsistent resolutions when opening the final graphics in Word or PowerPoint—if you specify a 5-inch wide image at 300 dpi, R incorrectly (for Office, at least) creates a PNG that will be huuuuge (like 20+ inches wide) when placed in Word. ([See here for more details.](https://mcfromnz.wordpress.com/2013/09/03/ggplot-powerpoint-wall-head-solution/)). Using `ggsave(..., type="cairo", dpi=300")` creates PNGs with correct resolutions and dimensions.

Example:


``` r
library(ggplot2)
library(Cairo)

df <- data.frame(x=1:10, y=rnorm(10))

p <- ggplot(df, aes(x=x, y=y)) +
  geom_point() + 
  labs(x="Something", y="Something else", title="This is a title",
       subtitle="Subtitle goes here", caption="Source: blah") + 
  theme_light(base_family="Source Sans Pro") + 
  theme(plot.title=element_text(family="Source Sans Pro Semibold"),
        plot.caption=element_text(family="Source Sans Pro Light"))

# Embed fonts with Cairo
ggsave(p, filename="~/Desktop/blah.pdf",
       width=4, height=3, units="in", device=cairo_pdf)

# Create high-DPI, anti-aliased PNG with correct fonts that works correctly in Word
ggsave(p, filename="~/Desktop/blah.png",
       width=4, height=3, units="in", type="cairo", dpi=300)

# Show image
p
```

![](http://i.imgur.com/s2W3mSZ.png)
