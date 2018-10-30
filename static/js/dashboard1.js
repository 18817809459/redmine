/*
Template Name: Admin Press Admin
Author: Themedesigner
Email: niravjoshi87@gmail.com
File: js
*/
$(function() {
    "use strict";
    // ============================================================== 
    // Sales overview
    // ============================================================== 
    Morris.Area({
        element: 'earning',
        data: [{
                period: '2011',
                Sales: 50,
            }, {
                period: '2012',
                Sales: 130,
            }, {
                period: '2013',
                Sales: 80,
            }, {
                period: '2014',
                Sales: 70,
            }, {
                period: '2015',
                Sales: 180,
            }, {
                period: '2016',
                Sales: 105,
            },
            {
                period: '2017',
                Sales: 250,
            }
        ],
        xkey: 'period',
        ykeys: ['Sales'],
        labels: ['Sales'],
        pointSize: 3,
        fillOpacity: 0,
        pointStrokeColors: ['#1976d2'],
        behaveLikeLine: true,
        gridLineColor: '#e0e0e0',
        lineWidth: 3,
        hideHover: 'auto',
        lineColors: ['#1976d2'],
        resize: true

    });

    // ============================================================== 
    // Sales overview
    // ==============================================================
    // ============================================================== 
    // Download count
    // ============================================================== 
    var sparklineLogin = function() {
        $('.spark-count').sparkline([4, 5, 0, 10, 9, 12, 4, 9, 4, 5, 3, 10, 9, 12, 10, 9], {
            type: 'bar',
            width: '100%',
            height: '50',
            barWidth: '2',
            resize: true,
            barSpacing: '5',
            barColor: 'rgba(255, 255, 255, 0.3)'
        });

        $('.spark-count2').sparkline([20, 40, 30], {
            type: 'pie',
            height: '90',
            resize: true,
            sliceColors: ['#1cadbf', '#1f5f67', '#ffffff']
        });
    }
    var sparkResize;

    sparklineLogin();


});