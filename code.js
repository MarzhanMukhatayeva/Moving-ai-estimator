// Google Apps Script for Moving AI Estimator
// Trigger: on form submit
// Sends data to Azure Function → receives estimate → writes to Sheet → sends email
function onFormSubmit(e) {
  const sheet = e.range.getSheet();
  const row = e.range.getRow();

  try {
    const data = e.namedValues;

    const fromAddress = data["From Address"] ? data["From Address"][0].trim() : "";
    const toAddress = data["To Address"] ? data["To Address"][0].trim() : "";
    const apartmentSize = data["Apartment Size"] ? data["Apartment Size"][0].trim() : "";
    const boxes = data["Boxes"] ? data["Boxes"][0].trim() : "";
    const stairs = data["Stairs"] ? data["Stairs"][0].trim() : "";
    const elevator = data["Elevator"] ? data["Elevator"][0].trim() : "";
    // Email берем прямо из таблицы, колонка H = 8
    const customerEmail = String(sheet.getRange(row, 8).getValue() || "").trim();
    Logger.log("customerEmail from sheet = " + customerEmail);
    Logger.log("DATA: " + JSON.stringify(data));
    Logger.log("EMAIL: " + customerEmail);

    // I=9, J=10, K=11, L=12
    if (!fromAddress || !toAddress) {
      sheet.getRange(row, 9).setValue("Missing address");
      sheet.getRange(row, 10).setValue("");
      sheet.getRange(row, 11).setValue("");
      sheet.getRange(row, 12).setValue("Stopped - missing address");
      return;
    }

    const payload = {
      from_address: fromAddress,
      to_address: toAddress,
      move_size: apartmentSize,
      boxes: boxes,
      stairs: stairs,
      elevator: elevator
    };

    const url = "AZURE_FUNCTION-URL";

    let response;
    try {
      response = UrlFetchApp.fetch(url, {
        method: "post",
        contentType: "application/json",
        payload: JSON.stringify(payload),
        muteHttpExceptions: true
      });
    } catch (error) {
      sheet.getRange(row, 9).setValue("Request failed");
      sheet.getRange(row, 10).setValue("");
      sheet.getRange(row, 11).setValue("");
      sheet.getRange(row, 12).setValue("Request failed - " + error.message);
      return;
    }

    const status = response.getResponseCode();
    const text = response.getContentText();

    Logger.log("Status: " + status);
    Logger.log("Response: " + text);

    if (!text || text.trim() === "") {
      sheet.getRange(row, 9).setValue("Empty response");
      sheet.getRange(row, 10).setValue("");
      sheet.getRange(row, 11).setValue("");
      sheet.getRange(row, 12).setValue("Stopped - empty response");
      return;
    }

    let result;
    try {
      result = JSON.parse(text);
    } catch (error) {
      sheet.getRange(row, 9).setValue("Invalid JSON");
      sheet.getRange(row, 10).setValue(text);
      sheet.getRange(row, 11).setValue("");
      sheet.getRange(row, 12).setValue("Stopped - invalid JSON");
      return;
    }

    if (result.error) {
      sheet.getRange(row, 9).setValue("Azure error");
      sheet.getRange(row, 10).setValue(result.error);
      sheet.getRange(row, 11).setValue("");
      sheet.getRange(row, 12).setValue("Stopped - Azure error");
      return;
    }

    const baseToFrom = formatRoute("Base → From", result.base_to_from);
    const toToBase = formatRoute("To → Base", result.to_to_base);

    sheet.getRange(row, 9).setValue(baseToFrom);
    sheet.getRange(row, 10).setValue(toToBase);

    let aiEmailText = "";
    if (result.ai_result && result.ai_result.estimate_text) {
      aiEmailText = result.ai_result.estimate_text;
    } else if (result.ai_result && result.ai_result.error_message) {
      aiEmailText = "AI error: " + result.ai_result.error_message;
    } else {
      aiEmailText = "No AI output";
    }

    sheet.getRange(row, 11).setValue(aiEmailText);

    if (!customerEmail) {
      sheet.getRange(row, 12).setValue("Not sent - no email");
      return;
    }

    const aiOk =
      result.ai_result &&
      (result.ai_result.status === "OK" || result.ai_result.status === "OK_TEXT_ONLY");

    if (!aiOk) {
      sheet.getRange(row, 12).setValue("Not sent - AI failed");
      return;
    }

    try {
      GmailApp.sendEmail(
        customerEmail,
        "Your Moving Estimate from Moving",
        aiEmailText
      );
      sheet.getRange(row, 12).setValue("Sent");
    } catch (error) {
      sheet.getRange(row, 12).setValue("Send failed - " + error.message);
    }

  } catch (error) {
    sheet.getRange(row, 12).setValue("Script crashed - " + error.message);
    Logger.log("FATAL ERROR: " + error.message);
  }
}

function formatRoute(title, route) {
  if (!route) return title + ": no data";

  if (route.error) {
    return title + " ERROR: " + route.error;
  }

  if (route.status && route.status !== "OK") {
    return title + " ERROR: " + route.status;
  }

  // Поддержка твоего текущего Python ответа
  if (route.minutes !== undefined && route.miles !== undefined) {
    return `${title}: ${route.minutes} min | ${route.miles} mi`;
  }

  if (route.duration_min !== undefined && route.distance_miles !== undefined) {
    return `${title}: ${route.duration_min} min | ${route.distance_miles} mi`;
  }

  return title + ": unexpected format";
}