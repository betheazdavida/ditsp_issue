/* global $, Highcharts */

function reversed (arr) {
  return arr.slice().reverse()
}

$(function () {
  var data = JSON.parse(document.querySelector('#graph-data').dataset.graph)

  var all = []
  var solved = []
  var unsolved = []

  var cAll = data.all
  var cSolved = data.solved

  reversed(data.monthData).forEach(function (m) {
    all.push(cAll)
    solved.push(cSolved)
    unsolved.push(cAll - cSolved)

    cAll -= m.created
    cSolved -= m.resolved - m.resets
  })

  all.reverse()
  solved.reverse()
  unsolved.reverse()

  var creates = data.monthData.map(function (m) {
    return m.created
  })
  var solves = data.monthData.map(function (m) {
    return m.resolved - m.resets
  })
  var captions = data.monthData.map(function (m) {
    return m.caption
  })

  Highcharts.chart('complain-total', {
    chart: {
      type: 'line'
    },
    title: {
      text: 'Ringkasan Keluhan'
    },
    xAxis: {
      categories: captions
    },
    yAxis: {
      title: {
        text: 'Jumlah'
      }
    },
    plotOptions: {
      line: {
        dataLabels: {
          enabled: true
        },
        enableMouseTracking: false
      }
    },
    series: [
      {
        name: 'Jumlah Keluhan',
        data: all
      },
      {
        name: 'Jumlah Keluhan Selesai',
        data: solved
      },
      {
        name: 'Jumlah Keluhan Belum Selesai',
        data: unsolved
      }
    ]
  })

  Highcharts.chart('complain-dispatched', {
    chart: {
      type: 'line'
    },
    title: {
      text: 'Penerimaan dan Penyelesaian Keluhan'
    },
    xAxis: {
      categories: captions
    },
    yAxis: {
      title: {
        text: 'Jumlah'
      }
    },
    plotOptions: {
      line: {
        dataLabels: {
          enabled: true
        },
        enableMouseTracking: false
      }
    },
    series: [
      {
        name: 'Jumlah Keluhan yang Masuk',
        data: creates
      },
      {
        name: 'Jumlah Keluhan yang Diselesaikan',
        data: solves
      }
    ]
  })
})
