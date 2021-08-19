/* globals Chart:false, feather:false, google:true */

let timerRefreshChart = null;
let isUpdating = false;

//let chartSensor = undefined;
let chartTemp = undefined;
let gaugeSensor = undefined;
let chartPress = undefined;
let chartLight = undefined;

(function () {
  'use strict'

  //Main
  feather.replace({ 'aria-hidden': 'true' })

  google.charts.load('current', {'packages':['corechart', 'gauge']});
  google.charts.setOnLoadCallback(drawTemp);
  //google.charts.setOnLoadCallback(drawGauge);
  google.charts.setOnLoadCallback(drawPress)
  google.charts.setOnLoadCallback(drawLight)



})()

function getSensorsNow(){
  isUpdating = true;
  fetch("/sensor_value")  // Sensor_Value - Caminho da API para retornar dados atuais do sensor - Implmentado no client
  .then((resp) => resp.json()) // Interpreta a resposta da requisição http na rota sensor_value como uma mensagem Json
  .then(function (data) {
      console.log(data) //Data é a resposta da requisão em json
      drawTemp(data.dadosgraficoT);
      //drawGauge(data.dadosgraficoT);
      drawPress(data.dadosgraficoP);
      drawLight(data.dadosgraficoL);

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
/*function drawGauge(newDados){
  let dados = google.visualization.arrayToDataTable([
    ['Label','Value'],
    ["...", 0]
  ]);

  //console.log(newDados)

  if(newDados !== undefined){
    dados = google.visualization.arrayToDataTable(newDados)
  }


  let options = {
    width: 400, height: 120,
    redFrom: 90, redTo: 100,
    yellowFrom:75, yellowTo: 90,
    minorTicks: 5
  };

  if(gaugeSensor === undefined){
    gaugeSensor = new google.visualization.Gauge(document.getElementById('chart_div'));
  }

  gaugeSensor.draw(dados,options)

  if(timerRefreshChart === null){
    timerRefreshChart = setTimeout(() => {
      console.log("[MAIN] Atualizando graficos");
      getSensorsNow();
    }, 1000)
  }
}*/

/*function drawChart(newData){
  let data = google.visualization.arrayToDataTable([
    ["Hora", "BMP-Temp.", "BMP-Press"],
    ["...", 0, 0]
  ]);


  if(newData !== undefined){
    data = google.visualization.arrayToDataTable(newData)
  }
  
  let options = {
    title: 'Dados',
    curveType: 'function',
    legend: { position: 'bottom' }
  };

  if(chartSensor === undefined){
    chartSensor = new google.visualization.LineChart(document.getElementById('myChart'));

  }

  chartSensor.draw(data, options);

  timerRefreshChart = setTimeout(() => {
    console.log("[MAIN] Atualizando graficos");
    getSensorsNow();
  }, 1000)
}*/

function drawTemp(newData){
  let data = google.visualization.arrayToDataTable([
    ["Hora", "BMP-Temp."],
    ["...", 0]
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
    ["Hora", "Light"],
    ["...", 0]
  ]);


  if(dadosLight !== undefined){
    dadosL = google.visualization.arrayToDataTable(dadosLight)
  }
  
  let options = {
    title: 'Light',
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



