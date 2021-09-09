let ddd = { "binData": [] };

let buildBinTitleElement = (data) => {
    let a = document.createElement("a");
    a.innerText = data.name + " (" + data.method + ")";
    a.title = data.src ? data.src : "" + data.url ? data.url : "" + data.info_url ? data.info_url : "";
    return a;

}

function onDataChanged() {
    document.getElementById("viewHeader").innerText = ddd.header;
    let p = ddd.profile;
    document.getElementById("viewProfileId").innerText = p.id;
    document.getElementById("profileDetailDevice").innerText = p.device ? p.device : "-";
    let binsDiv = document.getElementById("profileDetailBins");
    binsDiv.innerHTML = "";
    if (p.bins) {
        p.bins.forEach(b => {
            let d = document.createElement("div");
            d.appendChild(buildBinTitleElement(b));
            binsDiv.appendChild(d);
        });
    }
    let f = p.fuses ? p.fuses : {};
    document.getElementById("profileDetaiFuseHigh").innerText = f.hfuse ? f.hfuse : "-";
    document.getElementById("profileDetaiFuseLow").innerText = f.lfuse ? f.lfuse : "-";
    document.getElementById("profileDetaiFuseExt").innerText = f.efuse ? f.efuse : "-";
    document.getElementById("profileDetaiFuseLock").innerText = f.lock ? f.lock : "-";

    document.getElementById("profileDetailJumper").innerText = p.jumper ? p.jumper : "-";
    document.getElementById("profileDetailAutoDetect").innerText = p.autodetect ? "true" : "false";
    document.getElementById("profileDetailProfileType").innerText = p["type"];
    let s = ddd.serial;
    document.getElementById("profileDetailSerialPort").innerText = s.port;
    document.getElementById("profileDetailSerialEnable").innerText = s.enabled;
    document.getElementById("profileDetailSerialSpeed").innerText = s["speed"];
    let elms = document.querySelectorAll('[data-is-ser-related]');
    elms.forEach(e => e.disabled = !s.enabled);

}

function buildForm() {
    let root = document.getElementById("mainform");
    while (root.firstChild) {
        root.removeChild(root.firstChild);
    }
    clearLog('serialMonitor')
    let binData = ddd.binData;
    if (!binData.forEach) {
        return;
    }
    binData.forEach(f => {
        let div1 = document.createElement("div");
        div1.className = "formLine";
        let div2 = document.createElement("div");
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
    if (!ddd) {
        return;
    }
    ddd.binData.forEach(f => {
        d = document.getElementById("data_" + f.id);
        f.value = d.innerText;
    });
    payload = {
        "type": "form",
        "data": ddd.binData.map(o => {
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
            onDataChanged();
            buildForm()
        })
        .then(() => writeToLog("Data loaded from server"))
        .finally(() => writeSepToLog())
    fetch ("/profiles")
        .then(resp => resp.json())
        .then(loadProfiles)
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
sendCommand = (title,cmd) => {
    writeToLog("Sending " + title + " request")
    fetch('/' + cmd, { method: 'POST' })
        .then(async resp => {
            txt = await resp.text();
            if (resp.ok) {
                writeToLog(txt, null)
            } else {
                writeToLog(txt, "red")
            }
        })
        .catch ((e) => alert(e))
        .finally(() => writeSepToLog())

}

function doErase() {
    if (!confirm("Are you sure?")) {
        return;
    }
    sendCommand("Erase", "erase");
}

function loadProfiles(profiles) {
    let root = document.getElementById("divAllProfiles");
    while (root.firstChild) {
        root.removeChild(root.firstChild);
    }
    clearLog('serialMonitor')
    if (!profiles.forEach) {
        return;
    }
    let arr = profiles.map(p => {return {"id" : p.id, "device" : p.device, "jumper" : p.jumper? p.jumper : 10}});
    arr = arr.sort((a, b) => a.jumper - b.jumper);
    arr.forEach(p => {
        let d = document.createElement("div");
        let s = `${p.jumper<5 ? p.jumper : 'x'}: ${p.id} (${p.device})`
        let d1 = document.createElement("div");
        if (p.id === ddd.profile.id) {
            d1.style.fontWeight = "bold";
            d1.style.color = "blue";
        }
        d1.innerText = s;
        d.appendChild(d1);
        root.appendChild(d);
    })
}

