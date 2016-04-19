Title: Survey notes
Date: 2016-04-12
Modified: 2016-04-12
Highlight: True

# UX issues

Huge dropdown menus are a big UX problem, but smart people have invented [the ideal autocomplete country selector](http://baymard.com/labs/country-selector).

However, Qualtrics doesn't allow for complex forms with `data-alternative-spellings` and other custom attributes, so I can't use that cool system. I can use [generic jQuery UI autocomplete functions, though, and include a list of countries in Javascript](https://stackoverflow.com/questions/28952275/unsolved-adding-autocomplete-with-javascript-to-qualtrics).

In the header for the overall survey (under "Look and Feel"), add this:

```html
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquerymobile/1.4.5/jquery.mobile.min.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.3/jquery-ui.min.js"></script>
<script>
var $j = jQuery.noConflict();  
</script>
```

Then in the question itself, remove the `Qualtrics.SurveyEngine.addOnload(function()` and add:

```
$j(function() {
    var availableTags = [
        "Afghanistan",
        "Albania",
        "Algeria",
        "..."
    ];
    $j( ".InputText" ).autocomplete({
        source: availableTags
    });
});
```

*[Get the full list of countries here](/project/diss-ingos-in-autocracies/survey-countries/)*

Finally, the submenu needs some styling. Add this through the "Look and Feel" section:

```css
.ui-autocomplete {
    font-family: Roboto, "Helvetica Neue", Arial, sans-serif;
    padding: 0;
    list-style: none;
    background-color: #fff;
    width: 218px;
    border: 1px solid #B0BECA;
    max-height: 350px;
    overflow-x: hidden;
}

.ui-autocomplete .ui-menu-item {
    border-top: 1px solid #B0BECA;
    display: block;
    padding: 4px 6px;
    color: #353D44;
    cursor: pointer;
}

.ui-autocomplete .ui-menu-item:first-child {
    border-top: none;
}

.ui-autocomplete .ui-menu-item.ui-state-focus {
    background-color: #D5E5F4;
    color: #161A1C;
}
```
