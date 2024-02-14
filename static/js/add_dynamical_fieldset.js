let form_count = Number($("[name=form-TOTAL_FORMS]").val());

$("#add-another").click(function () {
    let field_id = `id_form-${form_count}-image_of_item`
    let element = $(`<label for="${field_id}">Image of item</label> <input id=${field_id} type="file" accept="image/*"></br>`);
    element.attr('name', `form-${form_count}-image_of_item`);
    $("#forms").append(element);
    form_count++;
    $("[name=form-TOTAL_FORMS]").val(form_count);
})