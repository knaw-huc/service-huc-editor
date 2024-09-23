let server = 'http://localhost/ccf/'

// let server = window.location.protocol + "//" + window.location.host + "/" + "ccf/";

// console.log('server: ', server);

var ccfOptions = {
    uploadButton: {
        actionURI: server + 'upload.php'
    },
    submitButton: {
        actionURI: 'create_record.php',
        label: 'Submit'
    },
    saveButton: {
        actionURI: 'create_record.php',
        label: 'Save'  
    },
    resetButton: {
        actionURI: 'javascript:history.back()',
        label: 'Back'
    },
    language: 'en',
    alert: {
      mandatory_field: 'This field is mandatory!',
      mandatory_field_box: ' : mandatory!',
      no_valid_date: 'This is not a valid date!',
      no_valid_date_box: ': not a valid date!',
      date_string: 'yyyy-mm-dd',
      anyURI_string: 'uri or url',
      int_field: 'The value of this field must be an integer!',
      int_field_box: 'must be an integer!',
      attr_not_empty_field: 'Attribute(s) mandatory'
    }
};



