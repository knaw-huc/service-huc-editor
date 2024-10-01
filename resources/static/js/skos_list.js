var skosListRegistry = {
    currentID: '',
    skosURI: ''
}

const reBind = () => {
    $(".skos-list-btn").each(function () {
        if (typeof this.onclick !== "function") {
            $(this).on('click', function () {
                skosListRegistry.currentID = $(this).parent().children().first().attr('id');
                skosListRegistry.URI = $(this).parent().children().first().attr("data-uri");

                var modal = document.getElementById("myModal");
                modal.style.display = "block";
                fill_skos_list('A');
            })
        }
    });
}

ccfTrackedFunctions.push(reBind);

function bind_skos_lists() {
    createSKOSListModal();
    $("input[data-class='skosType']").each(function () {
        var that = $(this);
        var el = document.createElement('span');
        el.innerHTML = "☰";
        $(el).addClass("skos-list-btn");
        $(el).on('click', function () {
            skosListRegistry.currentID = $(that).attr('id');
            skosListRegistry.skosURI = $(that).attr("data-uri");
            var modal = document.getElementById("myModal");
            modal.style.display = "block";
            fill_skos_list('A');
        })
        $(this).parent().append(el);
    });
}

function fill_skos_list(letter) {
    var host = window.location.protocol + '//' + window.location.host + skosListRegistry.skosURI + '?q=^' + letter;

    $.ajax({
        type: "GET",
        url: host,
        success: function (json) {
            obj = json;
            showLetterList(obj);
        },
        error: function (err) {
            obj = {"error": err};
            console.log(obj);
        }
    });
}

function showLetterList(obj) {

    if (obj.suggestions.length === 0) {
        $("#skos_list_picker").html('No values for this letter');
    } else {
        $("#skos_list_picker").html("");
        obj.suggestions.forEach(createListElement);
    }
}

function createListElement(value) {
    var el = document.createElement('div');
    $(el).addClass("skos-list-value");
    $(el).on("click", function () {
        $("#" + skosListRegistry.currentID).val(value);
        document.getElementById("myModal").style.display = "none";
    });
    $(el).html(value);
    $("#skos_list_picker").append(el);
}

function createSKOSListModal() {
    var modal = document.createElement('div');
    $(modal).attr('id', "myModal");
    $(modal).addClass("skos-list-modal");
    var content = document.createElement('div');
    $(content).addClass('skos-list-modal-content');
    var closeBtn = document.createElement('span');
    $(closeBtn).attr('id', 'skos-list-close');
    $(closeBtn).on('click', function () {
        document.getElementById("myModal").style.display = "none";
    })
    $(closeBtn).html('&times;');
    var modalBody = document.createElement('div');
    $(modalBody).append(append_letter_frame());
    $(modalBody).append(append_list_template());
    $(content).append(closeBtn);
    $(content).append(modalBody);
    $(modal).append(content);
    $('#wrapper').append(modal);
}


function append_letter_frame() {
    var letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    var letterFrame = document.createElement('div');
    $(letterFrame).attr('id', 'skosLetterFrame');
    for (let i = 0; i < letters.length; i++) {
        var obj = createLetterBtn(letters.charAt(i));
        $(letterFrame).append(obj);
    }
    $(letterFrame).append(create_skos_link());
    return letterFrame;
}

function append_list_template() {
    var obj = document.createElement('div');
    $(obj).attr('id', 'skos_list_picker');
    $(obj).html('Loading...');
    return obj;
}

function createLetterBtn(letter) {
    var letterBtn = document.createElement('div');
    $(letterBtn).addClass('skos_list_letterBtn');
    $(letterBtn).on("click", function () {
        fill_skos_list(letter);
    })
    $(letterBtn).html(letter);
    return letterBtn;
}

function create_skos_link() {
    var obj = document.createElement('div');
    $(obj).addClass('skos_list_letterBtn');
    $(obj).on("click", function () {
        window.open("https://skosmos.sd.di.huc.knaw.nl/" + skosListRegistry.skosURI.split('=')[1] + "/en/");
    })
    $(obj).html('Skosmos');
    return obj;
}