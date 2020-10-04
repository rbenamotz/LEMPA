ddd = {};

function buildForm() {
    root = document.getElementById("mainform");
    ddd.forEach(f => {
        div1 = document.createElement("div");
        div1.className = "formLine";
        div2 = document.createElement("div");
        div2.className = "formLine formValue"
        div2.id = "data_" + f.id;
        div1.innerText = f.title;
        div2.innerText = f.value;
        div2.contentEditable = true;
        root.appendChild(div1);
        root.appendChild(div2);
    })
}

function sendFormToSerial() {
    ddd.forEach(f => {
        d = document.getElementById("data_" + f.id);
        f.value = d.innerText;
    });
    payload = {
        "type": "form",
        "data": ddd.map(o => {
            return { "id": o.id, "value": o.value };
        })
    };
    sendDataToSerial(payload);
}

function sendTextToSerial(txt) {
    let payload = { "type": "text", "data": txt }
    sendDataToSerial(payload);
}


function sendDataToSerial(payload) {
    body = JSON.stringify(payload)
    writeToLog("Sending " + body)
    fetch('/data', { method: 'POST', body: body })
        .then(async resp => {
            txt = await resp.text();
            if (resp.ok) {
                writeToLog(txt, null)
            } else {
                writeToLog(txt, "red")
            }
        })
        .finally(() => writeSepToLog())
}

function onload() {
    fetch('/data')
        .then(resp => resp.json())
        .then(data => {
            ddd = data;
            buildForm()
        })
        .then(() => writeToLog("Data loaded from server"))
        .finally(() => writeSepToLog())
    var serialOutText = document.getElementById("serialOutText");
    serialOutText.addEventListener("keyup", onSerialOutTextKeyUp);
}

function writeToSerialMonitor(txt, preFix) {
    elm = document.getElementById("serialMonitor");
    let line = document.createElement("div");
    var spn1 = document.createElement("span");
    spn1.innerText = formatDate();
    var spn2 = document.createElement("span");
    spn2.className = "logDir";
    spn2.innerText = " " + preFix + " ";
    var spn3 = document.createElement("span");
    spn3.innerText = txt;
    line.appendChild(spn1);
    line.appendChild(spn2);
    line.appendChild(spn3);
    //line.innerText = formatDate() + " " + preFix + " " + txt;
    elm.appendChild(line);
    elm.scrollTo(0, elm.scrollHeight);
}

function writeToLog(txt, clr) {
    elm = document.getElementById("logDiv");
    line = document.createElement("div");
    line.innerText = formatDate() + " " + txt;
    if (clr)
        line.style.color = clr;
    elm.appendChild(line);
    elm.scrollTo(0, elm.scrollHeight);
}

function writeSepToLog() {
    pre = document.getElementById("logDiv");
    hr = document.createElement("hr");
    pre.appendChild(hr);
    pre.scrollTo(0, pre.scrollHeight);
}

function addLeadingZero(v) {
    if (v < 10) {
        return "0" + v;
    }
    return "" + v;
}

function formatDate() {
    var date = new Date()
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var sec = date.getSeconds();
    return addLeadingZero(hours) + ":" + addLeadingZero(minutes) + ":" + addLeadingZero(sec);
}

function serialoutKeyDown(args) {
    console.log(args)
}

function sendSerialTextFromForm() {
    var elm = document.getElementById("serialOutText")
    sendTextToSerial(elm.value);
    elm.focus();
    elm.select();
}

function onSerialOutTextKeyUp(event) {
    if (event.keyCode !== 13)
        return;
    sendSerialTextFromForm();
}

function clearLog(elementId) {
    elm = document.getElementById(elementId);
    while (elm.firstChild) {
        elm.removeChild(elm.firstChild);
    }
}
