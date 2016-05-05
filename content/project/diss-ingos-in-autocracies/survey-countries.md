Title: Possible countries in survey
Date: 2016-04-19
Modified: 2016-05-05 10:30:21
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
library(feather)      # For passing data between R scripts

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
         `COW code` = countrycode(ISO3, "iso3c", "cown")) %>%
  filter(!is.na(ISO3)) %>%
  mutate(`Qualtrics ID` = 1:n())
wb.countries.clean
#> Source: local data frame [212 x 4]
#> 
#>           Country name  ISO3 COW code Qualtrics ID
#>                  <chr> <chr>    <int>        <int>
#> 1          Afghanistan   AFG      700            1
#> 2              Albania   ALB      339            2
#> 3              Algeria   DZA      615            3
#> 4       American Samoa   ASM       NA            4
#> 5              Andorra   AND      232            5
#> 6               Angola   AGO      540            6
#> 7  Antigua and Barbuda   ATG       58            7
#> 8            Argentina   ARG      160            8
#> 9              Armenia   ARM      371            9
#> 10               Aruba   ABW       NA           10
#> ..                 ...   ...      ...          ...

# Nice Markdown table
pandoc.table.return(wb.countries.clean, justify="lccc") %>%
  cat(., file=file.path(PROJHOME, "Data", "Survey", "output", "survey_countries.md"))

# Regex for question validation
gsub("\\.", "\\\\.", paste(wb.countries.clean$`Country name`, collapse="|")) %>%
  cat(., file=file.path(PROJHOME, "Data", "Survey", "output", "survey_regex.txt"))

# Plain text list of countries for Qualtrics
cat(paste0(wb.countries.clean$`Country name`, collapse="\n"),
    file=file.path(PROJHOME, "Data", "Survey", "output", "survey_countries.txt"))

# Save as feather
write_feather(wb.countries.clean,
              path=file.path(PROJHOME, "Data", "Survey", "output",
                             "survey_countries.feather"))
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

Andorra                         AND      232           5       

Angola                          AGO      540           6       

Antigua and Barbuda             ATG       58           7       

Argentina                       ARG      160           8       

Armenia                         ARM      371           9       

Aruba                           ABW       NA           10      

Australia                       AUS      900           11      

Austria                         AUT      305           12      

Azerbaijan                      AZE      373           13      

Bahamas, The                    BHS       31           14      

Bahrain                         BHR      692           15      

Bangladesh                      BGD      771           16      

Barbados                        BRB       53           17      

Belarus                         BLR      370           18      

Belgium                         BEL      211           19      

Belize                          BLZ       80           20      

Benin                           BEN      434           21      

Bermuda                         BMU       NA           22      

Bhutan                          BTN      760           23      

Bolivia                         BOL      145           24      

Bosnia and Herzegovina          BIH      346           25      

Botswana                        BWA      571           26      

Brazil                          BRA      140           27      

Brunei Darussalam               BRN      835           28      

Bulgaria                        BGR      355           29      

Burkina Faso                    BFA      439           30      

Burundi                         BDI      516           31      

Cabo Verde                      CPV      402           32      

Cambodia                        KHM      811           33      

Cameroon                        CMR      471           34      

Canada                          CAN       20           35      

Cayman Islands                  CYM       NA           36      

Central African Republic        CAF      482           37      

Chad                            TCD      483           38      

Chile                           CHL      155           39      

China                           CHN      710           40      

Colombia                        COL      100           41      

Comoros                         COM      581           42      

Congo, Dem. Rep.                COD      490           43      

Congo, Rep.                     COG      484           44      

Costa Rica                      CRI       94           45      

Cote d'Ivoire                   CIV      437           46      

Croatia                         HRV      344           47      

Cuba                            CUB       40           48      

Curacao                         CUW       NA           49      

Cyprus                          CYP      352           50      

Czech Republic                  CZE      316           51      

Denmark                         DNK      390           52      

Djibouti                        DJI      522           53      

Dominica                        DMA       54           54      

Dominican Republic              DOM       42           55      

Ecuador                         ECU      130           56      

Egypt, Arab Rep.                EGY      651           57      

El Salvador                     SLV       92           58      

Equatorial Guinea               GNQ      411           59      

Eritrea                         ERI      531           60      

Estonia                         EST      366           61      

Ethiopia                        ETH      530           62      

Faroe Islands                   FRO       NA           63      

Fiji                            FJI      950           64      

Finland                         FIN      375           65      

France                          FRA      220           66      

French Polynesia                PYF       NA           67      

Gabon                           GAB      481           68      

Gambia, The                     GMB      420           69      

Georgia                         GEO      372           70      

Germany                         DEU      255           71      

Ghana                           GHA      452           72      

Greece                          GRC      350           73      

Greenland                       GRL       NA           74      

Grenada                         GRD       55           75      

Guam                            GUM       NA           76      

Guatemala                       GTM       90           77      

Guinea                          GIN      438           78      

Guinea-Bissau                   GNB      404           79      

Guyana                          GUY      110           80      

Haiti                           HTI       41           81      

Honduras                        HND       91           82      

Hong Kong SAR, China            HKG       NA           83      

Hungary                         HUN      310           84      

Iceland                         ISL      395           85      

India                           IND      750           86      

Indonesia                       IDN      850           87      

Iran, Islamic Rep.              IRN      630           88      

Iraq                            IRQ      645           89      

Ireland                         IRL      205           90      

Isle of Man                     IMN       NA           91      

Israel                          ISR      666           92      

Italy                           ITA      325           93      

Jamaica                         JAM       51           94      

Japan                           JPN      740           95      

Jordan                          JOR      663           96      

Kazakhstan                      KAZ      705           97      

Kenya                           KEN      501           98      

Kiribati                        KIR      946           99      

Korea, Dem. People’s Rep.       PRK      731          100      

Korea, Rep.                     KOR      732          101      

Kuwait                          KWT      690          102      

Kyrgyz Republic                 KGZ      703          103      

Lao PDR                         LAO      812          104      

Latvia                          LVA      367          105      

Lebanon                         LBN      660          106      

Lesotho                         LSO      570          107      

Liberia                         LBR      450          108      

Libya                           LBY      620          109      

Liechtenstein                   LIE      223          110      

Lithuania                       LTU      368          111      

Luxembourg                      LUX      212          112      

Macao SAR, China                MAC       NA          113      

Macedonia, FYR                  MKD      343          114      

Madagascar                      MDG      580          115      

Malawi                          MWI      553          116      

Malaysia                        MYS      820          117      

Maldives                        MDV      781          118      

Mali                            MLI      432          119      

Malta                           MLT      338          120      

Marshall Islands                MHL      983          121      

Mauritania                      MRT      435          122      

Mauritius                       MUS      590          123      

Mexico                          MEX       70          124      

Micronesia, Fed. Sts.           FSM      987          125      

Moldova                         MDA      359          126      

Monaco                          MCO      221          127      

Mongolia                        MNG      712          128      

Montenegro                      MNE      341          129      

Morocco                         MAR      600          130      

Mozambique                      MOZ      541          131      

Myanmar                         MMR      775          132      

Namibia                         NAM      565          133      

Nepal                           NPL      790          134      

Netherlands                     NLD      210          135      

New Caledonia                   NCL       NA          136      

New Zealand                     NZL      920          137      

Nicaragua                       NIC       93          138      

Niger                           NER      436          139      

Nigeria                         NGA      475          140      

Northern Mariana Islands        MNP       NA          141      

Norway                          NOR      385          142      

Oman                            OMN      698          143      

Pakistan                        PAK      770          144      

Palau                           PLW      986          145      

Panama                          PAN       95          146      

Papua New Guinea                PNG      910          147      

Paraguay                        PRY      150          148      

Peru                            PER      135          149      

Philippines                     PHL      840          150      

Poland                          POL      290          151      

Portugal                        PRT      235          152      

Puerto Rico                     PRI       NA          153      

Qatar                           QAT      694          154      

Romania                         ROU      360          155      

Russian Federation              RUS      365          156      

Rwanda                          RWA      517          157      

Samoa                           WSM      990          158      

San Marino                      SMR      331          159      

Sao Tome and Principe           STP      403          160      

Saudi Arabia                    SAU      670          161      

Senegal                         SEN      433          162      

Serbia                          SRB       NA          163      

Seychelles                      SYC      591          164      

Sierra Leone                    SLE      451          165      

Singapore                       SGP      830          166      

Sint Maarten (Dutch part)       SXM       NA          167      

Slovak Republic                 SVK      317          168      

Slovenia                        SVN      349          169      

Solomon Islands                 SLB      940          170      

Somalia                         SOM      520          171      

South Africa                    ZAF      560          172      

South Sudan                     SSD      626          173      

Spain                           ESP      230          174      

Sri Lanka                       LKA      780          175      

St. Kitts and Nevis             KNA       60          176      

St. Lucia                       LCA       56          177      

St. Martin (French part)        MAF       NA          178      

St. Vincent and the Grenadines  VCT       57          179      

Sudan                           SDN      625          180      

Suriname                        SUR      115          181      

Swaziland                       SWZ      572          182      

Sweden                          SWE      380          183      

Switzerland                     CHE      225          184      

Syrian Arab Republic            SYR      652          185      

Tajikistan                      TJK      702          186      

Tanzania                        TZA      510          187      

Thailand                        THA      800          188      

Timor-Leste                     TLS      860          189      

Togo                            TGO      461          190      

Tonga                           TON      955          191      

Trinidad and Tobago             TTO       52          192      

Tunisia                         TUN      616          193      

Turkey                          TUR      640          194      

Turkmenistan                    TKM      701          195      

Turks and Caicos Islands        TCA       NA          196      

Tuvalu                          TUV      947          197      

Uganda                          UGA      500          198      

Ukraine                         UKR      369          199      

United Arab Emirates            ARE      696          200      

United Kingdom                  GBR      200          201      

United States                   USA       2           202      

Uruguay                         URY      165          203      

Uzbekistan                      UZB      704          204      

Vanuatu                         VUT      935          205      

Venezuela, RB                   VEN      101          206      

Vietnam                         VNM      816          207      

Virgin Islands (U.S.)           VIR       NA          208      

West Bank and Gaza              PSE       NA          209      

Yemen, Rep.                     YEM      679          210      

Zambia                          ZMB      551          211      

Zimbabwe                        ZWE      552          212      
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
