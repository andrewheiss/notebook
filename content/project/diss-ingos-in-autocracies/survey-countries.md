Title: Possible countries in survey
Date: 2016-04-19
Modified: 2016-04-19 17:03:18
Slug: survey-countries
Tags: survey
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
  gather(key, `Country name`, everything()) %>%
  select(-key) %>%
  mutate(ISO3 = countrycode(`Country name`, "country.name", "iso3c"),
         `COW code` = countrycode(ISO3, "iso3c", "cown"),
         `Qualtrics ID` = 1:n()) %>%
  filter(!is.na(ISO3))
wb.countries.clean
#> Source: local data frame [212 x 4]
#> 
#>           Country name  ISO3 COW code Qualtrics ID
#>                  <chr> <chr>    <int>        <int>
#> 1          Afghanistan   AFG      700            1
#> 2              Albania   ALB      339            2
#> 3              Algeria   DZA      615            3
#> 4       American Samoa   ASM       NA            4
#> 5              Andorra   AND      232            6
#> 6               Angola   AGO      540            7
#> 7  Antigua and Barbuda   ATG       58            8
#> 8            Argentina   ARG      160            9
#> 9              Armenia   ARM      371           10
#> 10               Aruba   ABW       NA           11
#> ..                 ...   ...      ...          ...

# Nice Markdown table
pandoc.table.return(wb.countries.clean, justify="lccc") %>%
  cat(., file=file.path(PROJHOME, "Data", "data_raw", "Survey", "survey_countries.md"))

# Regex for question validation
gsub("\\.", "\\\\.", paste(wb.countries.clean$`Country name`, collapse="|")) %>% 
  cat(., file=file.path(PROJHOME, "Data", "data_raw", "Survey", "survey_regex.txt"))

# Plain text list of countries for Qualtrics
cat(paste0(wb.countries.clean$`Country name`, collapse="\n"),
    file=file.path(PROJHOME, "Data", "data_raw", "Survey", "survey_countries.txt"))
```

# Validation regex

    Afghanistan|Albania|Algeria|American Samoa|Andorra|Angola|Antigua and Barbuda|Argentina|Armenia|Aruba|Australia|Austria|Azerbaijan|Bahamas, The|Bahrain|Bangladesh|Barbados|Belarus|Belgium|Belize|Benin|Bermuda|Bhutan|Bolivia|Bosnia and Herzegovina|Botswana|Brazil|Brunei Darussalam|Bulgaria|Burkina Faso|Burundi|Cabo Verde|Cambodia|Cameroon|Canada|Cayman Islands|Central African Republic|Chad|Chile|China|Colombia|Comoros|Congo, Dem\. Rep\.|Congo, Rep\.|Costa Rica|Cote d'Ivoire|Croatia|Cuba|Curacao|Cyprus|Czech Republic|Denmark|Djibouti|Dominica|Dominican Republic|Ecuador|Egypt, Arab Rep\.|El Salvador|Equatorial Guinea|Eritrea|Estonia|Ethiopia|Faroe Islands|Fiji|Finland|France|French Polynesia|Gabon|Gambia, The|Georgia|Germany|Ghana|Greece|Greenland|Grenada|Guam|Guatemala|Guinea|Guinea-Bissau|Guyana|Haiti|Honduras|Hong Kong SAR, China|Hungary|Iceland|India|Indonesia|Iran, Islamic Rep\.|Iraq|Ireland|Isle of Man|Israel|Italy|Jamaica|Japan|Jordan|Kazakhstan|Kenya|Kiribati|Korea, Dem\. People’s Rep\.|Korea, Rep\.|Kuwait|Kyrgyz Republic|Lao PDR|Latvia|Lebanon|Lesotho|Liberia|Libya|Liechtenstein|Lithuania|Luxembourg|Macao SAR, China|Macedonia, FYR|Madagascar|Malawi|Malaysia|Maldives|Mali|Malta|Marshall Islands|Mauritania|Mauritius|Mexico|Micronesia, Fed\. Sts\.|Moldova|Monaco|Mongolia|Montenegro|Morocco|Mozambique|Myanmar|Namibia|Nepal|Netherlands|New Caledonia|New Zealand|Nicaragua|Niger|Nigeria|Northern Mariana Islands|Norway|Oman|Pakistan|Palau|Panama|Papua New Guinea|Paraguay|Peru|Philippines|Poland|Portugal|Puerto Rico|Qatar|Romania|Russian Federation|Rwanda|Samoa|San Marino|Sao Tome and Principe|Saudi Arabia|Senegal|Serbia|Seychelles|Sierra Leone|Singapore|Sint Maarten (Dutch part)|Slovak Republic|Slovenia|Solomon Islands|Somalia|South Africa|South Sudan|Spain|Sri Lanka|St\. Kitts and Nevis|St\. Lucia|St\. Martin (French part)|St\. Vincent and the Grenadines|Sudan|Suriname|Swaziland|Sweden|Switzerland|Syrian Arab Republic|Tajikistan|Tanzania|Thailand|Timor-Leste|Togo|Tonga|Trinidad and Tobago|Tunisia|Turkey|Turkmenistan|Turks and Caicos Islands|Tuvalu|Uganda|Ukraine|United Arab Emirates|United Kingdom|United States|Uruguay|Uzbekistan|Vanuatu|Venezuela, RB|Vietnam|Virgin Islands (U\.S\.)|West Bank and Gaza|Yemen, Rep\.|Zambia|Zimbabwe


# Lookup table

---------------------------------------------------------------
Country name                    ISO3   COW code   Qualtrics ID 
------------------------------ ------ ---------- --------------
Afghanistan                     AFG      700           1       

Albania                         ALB      339           2       

Algeria                         DZA      615           3       

American Samoa                  ASM       NA           4       

Andorra                         AND      232           6       

Angola                          AGO      540           7       

Antigua and Barbuda             ATG       58           8       

Argentina                       ARG      160           9       

Armenia                         ARM      371           10      

Aruba                           ABW       NA           11      

Australia                       AUS      900           12      

Austria                         AUT      305           13      

Azerbaijan                      AZE      373           14      

Bahamas, The                    BHS       31           15      

Bahrain                         BHR      692           16      

Bangladesh                      BGD      771           17      

Barbados                        BRB       53           18      

Belarus                         BLR      370           19      

Belgium                         BEL      211           20      

Belize                          BLZ       80           21      

Benin                           BEN      434           22      

Bermuda                         BMU       NA           23      

Bhutan                          BTN      760           24      

Bolivia                         BOL      145           25      

Bosnia and Herzegovina          BIH      346           26      

Botswana                        BWA      571           27      

Brazil                          BRA      140           28      

Brunei Darussalam               BRN      835           29      

Bulgaria                        BGR      355           30      

Burkina Faso                    BFA      439           31      

Burundi                         BDI      516           32      

Cabo Verde                      CPV      402           33      

Cambodia                        KHM      811           34      

Cameroon                        CMR      471           35      

Canada                          CAN       20           36      

Cayman Islands                  CYM       NA           37      

Central African Republic        CAF      482           38      

Chad                            TCD      483           39      

Chile                           CHL      155           40      

China                           CHN      710           41      

Colombia                        COL      100           42      

Comoros                         COM      581           43      

Congo, Dem. Rep.                COD      490           44      

Congo, Rep.                     COG      484           45      

Costa Rica                      CRI       94           46      

Cote d'Ivoire                   CIV      437           47      

Croatia                         HRV      344           48      

Cuba                            CUB       40           49      

Curacao                         CUW       NA           50      

Cyprus                          CYP      352           51      

Czech Republic                  CZE      316           52      

Denmark                         DNK      390           53      

Djibouti                        DJI      522           54      

Dominica                        DMA       54           55      

Dominican Republic              DOM       42           56      

Ecuador                         ECU      130           57      

Egypt, Arab Rep.                EGY      651           58      

El Salvador                     SLV       92           59      

Equatorial Guinea               GNQ      411           60      

Eritrea                         ERI      531           61      

Estonia                         EST      366           62      

Ethiopia                        ETH      530           63      

Faroe Islands                   FRO       NA           64      

Fiji                            FJI      950           65      

Finland                         FIN      375           66      

France                          FRA      220           67      

French Polynesia                PYF       NA           68      

Gabon                           GAB      481           69      

Gambia, The                     GMB      420           70      

Georgia                         GEO      372           71      

Germany                         DEU      255           72      

Ghana                           GHA      452           73      

Greece                          GRC      350           74      

Greenland                       GRL       NA           75      

Grenada                         GRD       55           76      

Guam                            GUM       NA           77      

Guatemala                       GTM       90           78      

Guinea                          GIN      438           79      

Guinea-Bissau                   GNB      404           80      

Guyana                          GUY      110           81      

Haiti                           HTI       41           82      

Honduras                        HND       91           83      

Hong Kong SAR, China            HKG       NA           84      

Hungary                         HUN      310           85      

Iceland                         ISL      395           86      

India                           IND      750           87      

Indonesia                       IDN      850           88      

Iran, Islamic Rep.              IRN      630           89      

Iraq                            IRQ      645           90      

Ireland                         IRL      205           91      

Isle of Man                     IMN       NA           92      

Israel                          ISR      666           93      

Italy                           ITA      325           94      

Jamaica                         JAM       51           95      

Japan                           JPN      740           96      

Jordan                          JOR      663           97      

Kazakhstan                      KAZ      705           98      

Kenya                           KEN      501           99      

Kiribati                        KIR      946          100      

Korea, Dem. People’s Rep.       PRK      731          101      

Korea, Rep.                     KOR      732          102      

Kuwait                          KWT      690          103      

Kyrgyz Republic                 KGZ      703          104      

Lao PDR                         LAO      812          105      

Latvia                          LVA      367          106      

Lebanon                         LBN      660          107      

Lesotho                         LSO      570          109      

Liberia                         LBR      450          110      

Libya                           LBY      620          111      

Liechtenstein                   LIE      223          112      

Lithuania                       LTU      368          113      

Luxembourg                      LUX      212          114      

Macao SAR, China                MAC       NA          115      

Macedonia, FYR                  MKD      343          116      

Madagascar                      MDG      580          117      

Malawi                          MWI      553          118      

Malaysia                        MYS      820          119      

Maldives                        MDV      781          120      

Mali                            MLI      432          121      

Malta                           MLT      338          122      

Marshall Islands                MHL      983          123      

Mauritania                      MRT      435          124      

Mauritius                       MUS      590          125      

Mexico                          MEX       70          126      

Micronesia, Fed. Sts.           FSM      987          127      

Moldova                         MDA      359          128      

Monaco                          MCO      221          129      

Mongolia                        MNG      712          130      

Montenegro                      MNE      341          131      

Morocco                         MAR      600          132      

Mozambique                      MOZ      541          133      

Myanmar                         MMR      775          134      

Namibia                         NAM      565          135      

Nepal                           NPL      790          136      

Netherlands                     NLD      210          137      

New Caledonia                   NCL       NA          138      

New Zealand                     NZL      920          139      

Nicaragua                       NIC       93          140      

Niger                           NER      436          141      

Nigeria                         NGA      475          142      

Northern Mariana Islands        MNP       NA          143      

Norway                          NOR      385          144      

Oman                            OMN      698          145      

Pakistan                        PAK      770          146      

Palau                           PLW      986          147      

Panama                          PAN       95          148      

Papua New Guinea                PNG      910          149      

Paraguay                        PRY      150          150      

Peru                            PER      135          151      

Philippines                     PHL      840          152      

Poland                          POL      290          153      

Portugal                        PRT      235          154      

Puerto Rico                     PRI       NA          155      

Qatar                           QAT      694          156      

Romania                         ROU      360          157      

Russian Federation              RUS      365          158      

Rwanda                          RWA      517          159      

Samoa                           WSM      990          160      

San Marino                      SMR      331          161      

Sao Tome and Principe           STP      403          163      

Saudi Arabia                    SAU      670          164      

Senegal                         SEN      433          165      

Serbia                          SRB       NA          166      

Seychelles                      SYC      591          167      

Sierra Leone                    SLE      451          168      

Singapore                       SGP      830          169      

Sint Maarten (Dutch part)       SXM       NA          170      

Slovak Republic                 SVK      317          171      

Slovenia                        SVN      349          172      

Solomon Islands                 SLB      940          173      

Somalia                         SOM      520          174      

South Africa                    ZAF      560          175      

South Sudan                     SSD      626          176      

Spain                           ESP      230          177      

Sri Lanka                       LKA      780          178      

St. Kitts and Nevis             KNA       60          179      

St. Lucia                       LCA       56          180      

St. Martin (French part)        MAF       NA          181      

St. Vincent and the Grenadines  VCT       57          182      

Sudan                           SDN      625          183      

Suriname                        SUR      115          184      

Swaziland                       SWZ      572          185      

Sweden                          SWE      380          186      

Switzerland                     CHE      225          187      

Syrian Arab Republic            SYR      652          188      

Tajikistan                      TJK      702          189      

Tanzania                        TZA      510          190      

Thailand                        THA      800          191      

Timor-Leste                     TLS      860          192      

Togo                            TGO      461          193      

Tonga                           TON      955          194      

Trinidad and Tobago             TTO       52          195      

Tunisia                         TUN      616          196      

Turkey                          TUR      640          197      

Turkmenistan                    TKM      701          198      

Turks and Caicos Islands        TCA       NA          199      

Tuvalu                          TUV      947          200      

Uganda                          UGA      500          201      

Ukraine                         UKR      369          202      

United Arab Emirates            ARE      696          203      

United Kingdom                  GBR      200          204      

United States                   USA       2           205      

Uruguay                         URY      165          206      

Uzbekistan                      UZB      704          207      

Vanuatu                         VUT      935          208      

Venezuela, RB                   VEN      101          209      

Vietnam                         VNM      816          210      

Virgin Islands (U.S.)           VIR       NA          211      

West Bank and Gaza              PSE       NA          212      

Yemen, Rep.                     YEM      679          213      

Zambia                          ZMB      551          214      

Zimbabwe                        ZWE      552          215      
---------------------------------------------------------------

# List for Qualtrics

- Afghanistan
- Albania
- Algeria
- American Samoa
- Andorra
- Angola
- Antigua and Barbuda
- Argentina
- Armenia
- Aruba
- Australia
- Austria
- Azerbaijan
- Bahamas, The
- Bahrain
- Bangladesh
- Barbados
- Belarus
- Belgium
- Belize
- Benin
- Bermuda
- Bhutan
- Bolivia
- Bosnia and Herzegovina
- Botswana
- Brazil
- Brunei Darussalam
- Bulgaria
- Burkina Faso
- Burundi
- Cabo Verde
- Cambodia
- Cameroon
- Canada
- Cayman Islands
- Central African Republic
- Chad
- Chile
- China
- Colombia
- Comoros
- Congo, Dem. Rep.
- Congo, Rep.
- Costa Rica
- Cote d'Ivoire
- Croatia
- Cuba
- Curacao
- Cyprus
- Czech Republic
- Denmark
- Djibouti
- Dominica
- Dominican Republic
- Ecuador
- Egypt, Arab Rep.
- El Salvador
- Equatorial Guinea
- Eritrea
- Estonia
- Ethiopia
- Faroe Islands
- Fiji
- Finland
- France
- French Polynesia
- Gabon
- Gambia, The
- Georgia
- Germany
- Ghana
- Greece
- Greenland
- Grenada
- Guam
- Guatemala
- Guinea
- Guinea-Bissau
- Guyana
- Haiti
- Honduras
- Hong Kong SAR, China
- Hungary
- Iceland
- India
- Indonesia
- Iran, Islamic Rep.
- Iraq
- Ireland
- Isle of Man
- Israel
- Italy
- Jamaica
- Japan
- Jordan
- Kazakhstan
- Kenya
- Kiribati
- Korea, Dem. People’s Rep.
- Korea, Rep.
- Kuwait
- Kyrgyz Republic
- Lao PDR
- Latvia
- Lebanon
- Lesotho
- Liberia
- Libya
- Liechtenstein
- Lithuania
- Luxembourg
- Macao SAR, China
- Macedonia, FYR
- Madagascar
- Malawi
- Malaysia
- Maldives
- Mali
- Malta
- Marshall Islands
- Mauritania
- Mauritius
- Mexico
- Micronesia, Fed. Sts.
- Moldova
- Monaco
- Mongolia
- Montenegro
- Morocco
- Mozambique
- Myanmar
- Namibia
- Nepal
- Netherlands
- New Caledonia
- New Zealand
- Nicaragua
- Niger
- Nigeria
- Northern Mariana Islands
- Norway
- Oman
- Pakistan
- Palau
- Panama
- Papua New Guinea
- Paraguay
- Peru
- Philippines
- Poland
- Portugal
- Puerto Rico
- Qatar
- Romania
- Russian Federation
- Rwanda
- Samoa
- San Marino
- Sao Tome and Principe
- Saudi Arabia
- Senegal
- Serbia
- Seychelles
- Sierra Leone
- Singapore
- Sint Maarten (Dutch part)
- Slovak Republic
- Slovenia
- Solomon Islands
- Somalia
- South Africa
- South Sudan
- Spain
- Sri Lanka
- St. Kitts and Nevis
- St. Lucia
- St. Martin (French part)
- St. Vincent and the Grenadines
- Sudan
- Suriname
- Swaziland
- Sweden
- Switzerland
- Syrian Arab Republic
- Tajikistan
- Tanzania
- Thailand
- Timor-Leste
- Togo
- Tonga
- Trinidad and Tobago
- Tunisia
- Turkey
- Turkmenistan
- Turks and Caicos Islands
- Tuvalu
- Uganda
- Ukraine
- United Arab Emirates
- United Kingdom
- United States
- Uruguay
- Uzbekistan
- Vanuatu
- Venezuela, RB
- Vietnam
- Virgin Islands (U.S.)
- West Bank and Gaza
- Yemen, Rep.
- Zambia
- Zimbabwe
