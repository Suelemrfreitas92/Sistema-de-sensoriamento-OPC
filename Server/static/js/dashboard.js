/* globals Chart:false, feather:false, google:true */

let timerRefreshChart = null;
let isUpdating = false;

//let chartSensor = undefined;
let chartTemp = undefined;
let chartUmi = undefined;
let gaugeSensor = undefined;
let chartPress = undefined;
let chartLight = undefined;

let actuatorEnabled = false;
let isRequestingActuatorChange = false;

(function () {
  'use strict'

  //Main
  feather.replace({ 'aria-hidden': 'true' })

  google.charts.load('current', {'packages':['corechart', 'gauge']});
  google.charts.setOnLoadCallback(drawTemp);
  google.charts.setOnLoadCallback(drawUmi);
  //google.charts.setOnLoadCallback(drawGauge);
  google.charts.setOnLoadCallback(drawPress)
  google.charts.setOnLoadCallback(drawLight)



})()

async function setActuator(activate){
  if(isRequestingActuatorChange === false){
    try {
      // Faz POST enviando JSON que diz se deve ou não ativar atuador
      isRequestingActuatorChange = true;
      let rawResponse = await fetch("/actuator", {
        method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({shouldEnable: activate})
      });
      
      if (!rawResponse.ok) // ou verifique por response.status
        throw new Error(response.statusText);

      let response = await rawResponse.json();
      actuatorEnabled = activate;
      switchEnableDisableBtnOutline();
      isRequestingActuatorChange = false;
    } catch (error) {
      alert("Falha de rede ao controlar atuador");
      isRequestingActuatorChange = false;
      console.error(error);
    }
  }
}

function switchEnableDisableBtnOutline(){
  enableBtn = document.getElementById("btnEnableActuator");
  disableBtn = document.getElementById("btnDisableActuator");

  if(actuatorEnabled === true){
    disableBtn.classList.remove("btn-danger");
    disableBtn.classList.add("btn-outline-danger");

    enableBtn.classList.remove("btn-outline-success");
    enableBtn.classList.add("btn-success");
  }else{
    disableBtn.classList.remove("btn-outline-danger");
    disableBtn.classList.add("btn-danger");
    
    enableBtn.classList.remove("btn-success");
    enableBtn.classList.add("btn-outline-success");
  }
}

function getSensorsNow(){
  isUpdating = true;
  fetch("/sensor_value")  // Sensor_Value - Caminho da API para retornar dados atuais do sensor - Implmentado no server http
  .then((resp) => resp.json()) // Interpreta a resposta da requisição http na rota sensor_value como uma mensagem Json
  .then(function (data) {
      console.log(data) //Data é a resposta da requisão em json
      drawTemp(data.dadosgraficoT);
      drawUmi(data.dadosgraficoU);
      //drawGauge(data.dadosgraficoT);
      drawPress(data.dadosgraficoP);
      drawLight(data.dadosgraficoL);
      dataTemp = data.dadosgraficoT[data.dadosgraficoT.length-1][0];
      dataUmi = data.dadosgraficoU[data.dadosgraficoU.length-1][0];
      dataPress = data.dadosgraficoP[data.dadosgraficoP.length-1][0];
      dataLight = data.dadosgraficoL[data.dadosgraficoL.length-1][0];
      dataTemp1 = data.dadosgraficoT[data.dadosgraficoT.length-1][0];

      temperaturaAtual = data.dadosgraficoT[data.dadosgraficoT.length-1][1];
      temperaturaAtual1 = data.dadosgraficoT[data.dadosgraficoT.length-1][2];
      umidadeAtual = data.dadosgraficoU[data.dadosgraficoU.length-1][1];
      pressaoAtual = data.dadosgraficoP[data.dadosgraficoP.length-1][1];
      lightAtual = data.dadosgraficoL[data.dadosgraficoL.length-1][1];
      updateInterfaceValue(dataTemp,dataUmi,dataPress,dataLight,dataTemp1,temperaturaAtual,temperaturaAtual1,umidadeAtual,pressaoAtual,lightAtual);

      isUpdating = false;
      timerRefreshChart = setTimeout(() => {
        console.log("[MAIN] Atualizando graficos");
        getSensorsNow();
      }, 1000)
  })
  .catch(function (error) { // se der erro entra nesta condição
      console.log(error);
  });
}

function drawTemp(newData){
  let data = google.visualization.arrayToDataTable([
    ["Hora", "BMP-Temp.", "DHT11Temp."],
    ["...", 0, 0]
  ]);


  if(newData !== undefined){
    data = google.visualization.arrayToDataTable(newData)
  }
  
  let options = {
    title: 'TEMPERATURA',
    curveType: 'function',
    legend: { position: 'bottom' }
  };

  if(chartTemp === undefined){
    chartTemp = new google.visualization.LineChart(document.getElementById('myChartT'));

  }

  chartTemp.draw(data, options);

  if(timerRefreshChart === null){
    timerRefreshChart = setTimeout(() => {
      console.log("[MAIN] Atualizando graficos");
      getSensorsNow();
    }, 1000)
  }
}

function drawUmi(newData){
  let data = google.visualization.arrayToDataTable([
    ["Hora", "DHT11Umi."],
    ["...", 0]
  ]);

  if(newData !== undefined){
    data = google.visualization.arrayToDataTable(newData)
  }
  
  let options = {
    title: 'UMIDADE',
    curveType: 'function',
    legend: { position: 'bottom' }
  };

  if(chartUmi === undefined){
    chartUmi = new google.visualization.LineChart(document.getElementById('myChartU'));

  }

  chartUmi.draw(data, options);

  if(timerRefreshChart === null){
    timerRefreshChart = setTimeout(() => {
      console.log("[MAIN] Atualizando graficos");
      getSensorsNow();
    }, 1000)
  }
}


function drawPress(dadosPress){
  let dadosP = google.visualization.arrayToDataTable([
    ["Hora", "BMP-Pressao."],
    ["...", 0]
  ]);


  if(dadosPress !== undefined){
    dadosP = google.visualization.arrayToDataTable(dadosPress)
  }
  
  let options = {
    title: 'PRESSÃO',
    curveType: 'function',
    legend: { position: 'bottom' }
  };

  if(chartPress === undefined){
    chartPress = new google.visualization.LineChart(document.getElementById('myChartP'));

  }

  chartPress.draw(dadosP, options);

  if(timerRefreshChart === null){
    timerRefreshChart = setTimeout(() => {
      console.log("[MAIN] Atualizando graficos");
      getSensorsNow();
    }, 1000)
  }
}


function drawLight(dadosLight){
  let dadosL = google.visualization.arrayToDataTable([
    ["Hora", "Poti"],
    ["...", 0]
  ]);


  if(dadosLight !== undefined){
    dadosL = google.visualization.arrayToDataTable(dadosLight)
  }
  
  let options = {
    title: 'Potenciometro',
    curveType: 'function',
    legend: { position: 'bottom' }
  };

  if(chartLight === undefined){
    chartLight = new google.visualization.LineChart(document.getElementById('myChartL'));

  }

  chartLight.draw(dadosL, options);

  if(timerRefreshChart === null){
    timerRefreshChart = setTimeout(() => {
      console.log("[MAIN] Atualizando graficos");
      getSensorsNow();
    }, 1000)
  }
  
}

function updateInterfaceValue(dataVal,dataVal1,dataVal2,dataVal3,dataVal4,tempVal,temp1Val,umiVal,pressVal,lightVal)
{
  let dataLabel = document.getElementById('dataLabel');
  let dataLabel1 = document.getElementById('dataLabel1');
  let dataLabel2 = document.getElementById('dataLabel2');
  let dataLabel3 = document.getElementById('dataLabel3');
  let dataLabel4 = document.getElementById('dataLabel4');

  let tempLabel = document.getElementById('BMPTempLabel');
  let temp1Label = document.getElementById('DHT11TempLabel');
  let umidade = document.getElementById('DHT11UmiLabel');
  let pressLabel = document.getElementById('BMPPressLabel');
  let lightLabel = document.getElementById('lightLabel');


  dataLabel.innerHTML = dataVal;
  dataLabel1.innerHTML = dataVal1;
  dataLabel2.innerHTML = dataVal2;
  dataLabel3.innerHTML = dataVal3;
  dataLabel4.innerHTML = dataVal4

  tempLabel.innerHTML = tempVal;
  temp1Label.innerHTML = temp1Val;
  umidade.innerHTML = umiVal;
  pressLabel.innerHTML = pressVal;
  lightLabel.innerHTML = lightVal;

  //console.log(lightVal);
}




