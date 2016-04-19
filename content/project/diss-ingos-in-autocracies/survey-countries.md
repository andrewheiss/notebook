Title: Possible countries in survey
Date: 2016-04-19
Modified: 2016-04-19 00:25:38
Slug: survey-countries
Highlight: True

List of 212 countries taken from the [World Bank](http://data.worldbank.org/country)

# Code

``` r
library(dplyr)        # For magic dataframe manipulation
library(tidyr)        # For more magic dataframe manipulation
library(countrycode)  # Standardize countries
library(rvest)        # Scrape stuff from the web
library(pander)       # Markdown

# World Bank countries
wb.countries.raw <- read_html("http://data.worldbank.org/country") %>%
  html_nodes(xpath='//*[@id="block-views-countries-block_1"]/div/div/div/table') %>%
  html_table() %>% bind_rows() %>% as_data_frame()
wb.countries.raw
#> Source: local data frame [54 x 4]
#> 
#>                     X1                 X2               X3
#>                  <chr>              <chr>            <chr>
#> 1          Afghanistan           Dominica          Lesotho
#> 2              Albania Dominican Republic          Liberia
#> 3              Algeria            Ecuador            Libya
#> 4       American Samoa   Egypt, Arab Rep.    Liechtenstein
#> 5        Andean Region        El Salvador        Lithuania
#> 6              Andorra  Equatorial Guinea       Luxembourg
#> 7               Angola            Eritrea Macao SAR, China
#> 8  Antigua and Barbuda            Estonia   Macedonia, FYR
#> 9            Argentina           Ethiopia       Madagascar
#> 10             Armenia      Faroe Islands           Malawi
#> ..                 ...                ...              ...
#> Variables not shown: X4 <chr>.

# Clean up list of countries and add standard codes
wb.countries.clean <- wb.countries.raw %>%
  # The table from their website uses four columns; gather those into one 
  gather(key, country.name, everything()) %>%
  select(-key) %>%
  mutate(iso3 = countrycode(country.name, "country.name", "iso3c"),
         cowcode = countrycode(iso3, "iso3c", "cown")) %>%
  filter(!is.na(iso3))
wb.countries.clean
#> Source: local data frame [212 x 3]
#> 
#>           country.name  iso3 cowcode
#>                  <chr> <chr>   <int>
#> 1          Afghanistan   AFG     700
#> 2              Albania   ALB     339
#> 3              Algeria   DZA     615
#> 4       American Samoa   ASM      NA
#> 5              Andorra   AND     232
#> 6               Angola   AGO     540
#> 7  Antigua and Barbuda   ATG      58
#> 8            Argentina   ARG     160
#> 9              Armenia   ARM     371
#> 10               Aruba   ABW      NA
#> ..                 ...   ...     ...

# Nice Markdown table
pandoc.table.return(rename(wb.countries.clean, `Country name` = country.name, 
                           ISO3 = iso3, `COW code` = cowcode), 
                    justify="lcc") %>%
  cat(., file=file.path(PROJHOME, "Data", "data_raw", "Survey", "survey_countries.md"))

# Regex for question validation
gsub("\\.", "\\\\.", paste(wb.countries.clean$country.name, collapse="|")) %>% 
  cat(., file=file.path(PROJHOME, "Data", "data_raw", "Survey", "survey_regex.txt"))
```

# Validation regex

    Afghanistan|Albania|Algeria|American Samoa|Andorra|Angola|Antigua and Barbuda|Argentina|Armenia|Aruba|Australia|Austria|Azerbaijan|Bahamas, The|Bahrain|Bangladesh|Barbados|Belarus|Belgium|Belize|Benin|Bermuda|Bhutan|Bolivia|Bosnia and Herzegovina|Botswana|Brazil|Brunei Darussalam|Bulgaria|Burkina Faso|Burundi|Cabo Verde|Cambodia|Cameroon|Canada|Cayman Islands|Central African Republic|Chad|Chile|China|Colombia|Comoros|Congo, Dem\. Rep\.|Congo, Rep\.|Costa Rica|Cote d'Ivoire|Croatia|Cuba|Curacao|Cyprus|Czech Republic|Denmark|Djibouti|Dominica|Dominican Republic|Ecuador|Egypt, Arab Rep\.|El Salvador|Equatorial Guinea|Eritrea|Estonia|Ethiopia|Faroe Islands|Fiji|Finland|France|French Polynesia|Gabon|Gambia, The|Georgia|Germany|Ghana|Greece|Greenland|Grenada|Guam|Guatemala|Guinea|Guinea-Bissau|Guyana|Haiti|Honduras|Hong Kong SAR, China|Hungary|Iceland|India|Indonesia|Iran, Islamic Rep\.|Iraq|Ireland|Isle of Man|Israel|Italy|Jamaica|Japan|Jordan|Kazakhstan|Kenya|Kiribati|Korea, Dem\. People’s Rep\.|Korea, Rep\.|Kuwait|Kyrgyz Republic|Lao PDR|Latvia|Lebanon|Lesotho|Liberia|Libya|Liechtenstein|Lithuania|Luxembourg|Macao SAR, China|Macedonia, FYR|Madagascar|Malawi|Malaysia|Maldives|Mali|Malta|Marshall Islands|Mauritania|Mauritius|Mexico|Micronesia, Fed\. Sts\.|Moldova|Monaco|Mongolia|Montenegro|Morocco|Mozambique|Myanmar|Namibia|Nepal|Netherlands|New Caledonia|New Zealand|Nicaragua|Niger|Nigeria|Northern Mariana Islands|Norway|Oman|Pakistan|Palau|Panama|Papua New Guinea|Paraguay|Peru|Philippines|Poland|Portugal|Puerto Rico|Qatar|Romania|Russian Federation|Rwanda|Samoa|San Marino|Sao Tome and Principe|Saudi Arabia|Senegal|Serbia|Seychelles|Sierra Leone|Singapore|Sint Maarten (Dutch part)|Slovak Republic|Slovenia|Solomon Islands|Somalia|South Africa|South Sudan|Spain|Sri Lanka|St\. Kitts and Nevis|St\. Lucia|St\. Martin (French part)|St\. Vincent and the Grenadines|Sudan|Suriname|Swaziland|Sweden|Switzerland|Syrian Arab Republic|Tajikistan|Tanzania|Thailand|Timor-Leste|Togo|Tonga|Trinidad and Tobago|Tunisia|Turkey|Turkmenistan|Turks and Caicos Islands|Tuvalu|Uganda|Ukraine|United Arab Emirates|United Kingdom|United States|Uruguay|Uzbekistan|Vanuatu|Venezuela, RB|Vietnam|Virgin Islands (U\.S\.)|West Bank and Gaza|Yemen, Rep\.|Zambia|Zimbabwe


# List

------------------------------------------------
Country name                    ISO3   COW code 
------------------------------ ------ ----------
Afghanistan                     AFG      700    

Albania                         ALB      339    

Algeria                         DZA      615    

American Samoa                  ASM       NA    

Andorra                         AND      232    

Angola                          AGO      540    

Antigua and Barbuda             ATG       58    

Argentina                       ARG      160    

Armenia                         ARM      371    

Aruba                           ABW       NA    

Australia                       AUS      900    

Austria                         AUT      305    

Azerbaijan                      AZE      373    

Bahamas, The                    BHS       31    

Bahrain                         BHR      692    

Bangladesh                      BGD      771    

Barbados                        BRB       53    

Belarus                         BLR      370    

Belgium                         BEL      211    

Belize                          BLZ       80    

Benin                           BEN      434    

Bermuda                         BMU       NA    

Bhutan                          BTN      760    

Bolivia                         BOL      145    

Bosnia and Herzegovina          BIH      346    

Botswana                        BWA      571    

Brazil                          BRA      140    

Brunei Darussalam               BRN      835    

Bulgaria                        BGR      355    

Burkina Faso                    BFA      439    

Burundi                         BDI      516    

Cabo Verde                      CPV      402    

Cambodia                        KHM      811    

Cameroon                        CMR      471    

Canada                          CAN       20    

Cayman Islands                  CYM       NA    

Central African Republic        CAF      482    

Chad                            TCD      483    

Chile                           CHL      155    

China                           CHN      710    

Colombia                        COL      100    

Comoros                         COM      581    

Congo, Dem. Rep.                COD      490    

Congo, Rep.                     COG      484    

Costa Rica                      CRI       94    

Cote d'Ivoire                   CIV      437    

Croatia                         HRV      344    

Cuba                            CUB       40    

Curacao                         CUW       NA    

Cyprus                          CYP      352    

Czech Republic                  CZE      316    

Denmark                         DNK      390    

Djibouti                        DJI      522    

Dominica                        DMA       54    

Dominican Republic              DOM       42    

Ecuador                         ECU      130    

Egypt, Arab Rep.                EGY      651    

El Salvador                     SLV       92    

Equatorial Guinea               GNQ      411    

Eritrea                         ERI      531    

Estonia                         EST      366    

Ethiopia                        ETH      530    

Faroe Islands                   FRO       NA    

Fiji                            FJI      950    

Finland                         FIN      375    

France                          FRA      220    

French Polynesia                PYF       NA    

Gabon                           GAB      481    

Gambia, The                     GMB      420    

Georgia                         GEO      372    

Germany                         DEU      255    

Ghana                           GHA      452    

Greece                          GRC      350    

Greenland                       GRL       NA    

Grenada                         GRD       55    

Guam                            GUM       NA    

Guatemala                       GTM       90    

Guinea                          GIN      438    

Guinea-Bissau                   GNB      404    

Guyana                          GUY      110    

Haiti                           HTI       41    

Honduras                        HND       91    

Hong Kong SAR, China            HKG       NA    

Hungary                         HUN      310    

Iceland                         ISL      395    

India                           IND      750    

Indonesia                       IDN      850    

Iran, Islamic Rep.              IRN      630    

Iraq                            IRQ      645    

Ireland                         IRL      205    

Isle of Man                     IMN       NA    

Israel                          ISR      666    

Italy                           ITA      325    

Jamaica                         JAM       51    

Japan                           JPN      740    

Jordan                          JOR      663    

Kazakhstan                      KAZ      705    

Kenya                           KEN      501    

Kiribati                        KIR      946    

Korea, Dem. People’s Rep.       PRK      731    

Korea, Rep.                     KOR      732    

Kuwait                          KWT      690    

Kyrgyz Republic                 KGZ      703    

Lao PDR                         LAO      812    

Latvia                          LVA      367    

Lebanon                         LBN      660    

Lesotho                         LSO      570    

Liberia                         LBR      450    

Libya                           LBY      620    

Liechtenstein                   LIE      223    

Lithuania                       LTU      368    

Luxembourg                      LUX      212    

Macao SAR, China                MAC       NA    

Macedonia, FYR                  MKD      343    

Madagascar                      MDG      580    

Malawi                          MWI      553    

Malaysia                        MYS      820    

Maldives                        MDV      781    

Mali                            MLI      432    

Malta                           MLT      338    

Marshall Islands                MHL      983    

Mauritania                      MRT      435    

Mauritius                       MUS      590    

Mexico                          MEX       70    

Micronesia, Fed. Sts.           FSM      987    

Moldova                         MDA      359    

Monaco                          MCO      221    

Mongolia                        MNG      712    

Montenegro                      MNE      341    

Morocco                         MAR      600    

Mozambique                      MOZ      541    

Myanmar                         MMR      775    

Namibia                         NAM      565    

Nepal                           NPL      790    

Netherlands                     NLD      210    

New Caledonia                   NCL       NA    

New Zealand                     NZL      920    

Nicaragua                       NIC       93    

Niger                           NER      436    

Nigeria                         NGA      475    

Northern Mariana Islands        MNP       NA    

Norway                          NOR      385    

Oman                            OMN      698    

Pakistan                        PAK      770    

Palau                           PLW      986    

Panama                          PAN       95    

Papua New Guinea                PNG      910    

Paraguay                        PRY      150    

Peru                            PER      135    

Philippines                     PHL      840    

Poland                          POL      290    

Portugal                        PRT      235    

Puerto Rico                     PRI       NA    

Qatar                           QAT      694    

Romania                         ROU      360    

Russian Federation              RUS      365    

Rwanda                          RWA      517    

Samoa                           WSM      990    

San Marino                      SMR      331    

Sao Tome and Principe           STP      403    

Saudi Arabia                    SAU      670    

Senegal                         SEN      433    

Serbia                          SRB       NA    

Seychelles                      SYC      591    

Sierra Leone                    SLE      451    

Singapore                       SGP      830    

Sint Maarten (Dutch part)       SXM       NA    

Slovak Republic                 SVK      317    

Slovenia                        SVN      349    

Solomon Islands                 SLB      940    

Somalia                         SOM      520    

South Africa                    ZAF      560    

South Sudan                     SSD      626    

Spain                           ESP      230    

Sri Lanka                       LKA      780    

St. Kitts and Nevis             KNA       60    

St. Lucia                       LCA       56    

St. Martin (French part)        MAF       NA    

St. Vincent and the Grenadines  VCT       57    

Sudan                           SDN      625    

Suriname                        SUR      115    

Swaziland                       SWZ      572    

Sweden                          SWE      380    

Switzerland                     CHE      225    

Syrian Arab Republic            SYR      652    

Tajikistan                      TJK      702    

Tanzania                        TZA      510    

Thailand                        THA      800    

Timor-Leste                     TLS      860    

Togo                            TGO      461    

Tonga                           TON      955    

Trinidad and Tobago             TTO       52    

Tunisia                         TUN      616    

Turkey                          TUR      640    

Turkmenistan                    TKM      701    

Turks and Caicos Islands        TCA       NA    

Tuvalu                          TUV      947    

Uganda                          UGA      500    

Ukraine                         UKR      369    

United Arab Emirates            ARE      696    

United Kingdom                  GBR      200    

United States                   USA       2     

Uruguay                         URY      165    

Uzbekistan                      UZB      704    

Vanuatu                         VUT      935    

Venezuela, RB                   VEN      101    

Vietnam                         VNM      816    

Virgin Islands (U.S.)           VIR       NA    

West Bank and Gaza              PSE       NA    

Yemen, Rep.                     YEM      679    

Zambia                          ZMB      551    

Zimbabwe                        ZWE      552    
------------------------------------------------

