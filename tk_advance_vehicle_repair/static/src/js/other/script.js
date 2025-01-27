/** @odoo-module **/
import { jsonrpc } from "@web/core/network/rpc_service";
$(document).ready(function () {
    $("#country_id").on("change", function () {
        var text = "<option value='' selected='selected'>Select State</option>"
        var countryId = $(this).val();
        jsonrpc("/get_country_wise_state", {
            country_id: countryId
        }).then(function (country_wise_state) {
            if (country_wise_state) {
                for (var key in country_wise_state) {
                    text = text + '<option value="' + key + '">' + country_wise_state[key] + '</option>'
                }
                $('#state_id').empty().append(text);
            }
        });
    });
});

//vehicle brand wise model
$("#vehicle_brand_id").on("change", function () {
    var text = "<option value='' selected='selected'>Select Model</option>";
    var brandId = $(this).val();
    jsonrpc("/get_vehicle_model", {
        vehicle_brand_id: brandId
    }).then(function (vehicle_model) {
        if (vehicle_model) {
            for (var key in vehicle_model) {
                text += '<option value="' + key + '">' + vehicle_model[key] + '</option>';
            }
            $('#vehicle_model_id').empty().append(text);
        }
    });
});

// select register vehicle
$('#register_vehicle_id').change(function () {
    var regVehicleId = $('#register_vehicle_id').val();
    jsonrpc("/get_registered_vehicles", {
        'register_vehicle_id': regVehicleId
    }).then(function (result) {
        // Check if result is available
        if (result) {
            $('#vehicle_brand_id').val(result.vehicle_brand_id || '');
            $('#vehicle_model_id').val(result.vehicle_model_id || '');
            $('#vehicle_fuel_type_id').val(result.vehicle_fuel_type_id || '');
            $('#vin_no').val(result.vin_no || '');
            $('#registration_no').val(result.registration_no || '');
            $('.transmission_type').val(result.transmission_type || '');

            if (result.transmission_type === 'manual') {
                $('#manual').prop('checked', true);
                $('#automatic').prop('checked', false);
                $('#cvt').prop('checked', false);
            } else if (result.transmission_type === 'automatic') {
                $('#automatic').prop('checked', true);
                $('#manual').prop('checked', false);
                $('#cvt').prop('checked', false);
            } else {
                $('#cvt').prop('checked', true);
                $('#automatic').prop('checked', false);
                $('#manual').prop('checked', false);
            }
        } else {
            resetFields();
        }
    });
});

// Reset all fields to empty
function resetFields() {
    $('#vehicle_brand_id, #vehicle_model_id, #vehicle_fuel_type_id, #registration_no, #vin_no, .transmission_type').val('');
    $('#manual, #automatic, #cvt').prop('checked', false);
}
// fleet from onchange
$("#new").on("change", function () {
    resetFields();
    $('#from_fleet_vehicle, #from_customer_vehicle').addClass('d-none');
});

$("#customer_vehicle").on("change", function () {
    resetFields();
    $('#from_fleet_vehicle').addClass('d-none');
    $('#from_customer_vehicle').removeClass('d-none');
});

//Select Slot
function convertToTime(e) {
    const floatTime = e;
    const hours = Math.floor(floatTime);
    const minutes = (floatTime - hours) * 60;
    const formattedTime = `${hours.toString().padStart(2, '0')}:${Math.round(minutes).toString().padStart(2, '0')}`;
    return formattedTime
}

$('#booking_date').on("change", function () {
    $('#booking_appointment_slot_id').empty();
    let text = '<option selected="selected" value="">Select Slot</option>'
    var selectedDate = $("#booking_date").val();
    jsonrpc('/get_booking_day', {
        'selected_date': selectedDate
    }).then(function (result) {
        if (result['from_time'][0]) {
            $('#alert').addClass('d-none')
            $('#booking_slot_main').removeClass('d-none')
            result['from_time'].map((e, i) => {
                let first_time = convertToTime(e)
                let second_time = convertToTime(result['to_time'][i])
                text += `<option class="dynamic_slot" value="${result['slot_id'][i]}">
                            ${first_time} - ${second_time}
                        </option>`
            })
            $('#booking_appointment_slot_id').append(text)
        } else {
            $('#alert').removeClass('d-none')
            $('#booking_slot_main').addClass('d-none')
        }
    });
});