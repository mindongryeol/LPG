/**
 * Created by USER on 2016-11-21.
 */
var express = require('express');
var router = express.Router();
var mysql = require('mysql');
var pool = mysql.createPool({
    connectionLimit: 10,
    host: 'localhost',
    user: 'root',
    database: 'auction',
    password: '32166115'
});

router.get('/',function(req, res, next) {
   res.render('register');
});

router.post('/',function(req, res, next){
    console.log(req.body.id, req.body.pa);
    pool.getConnection(function (err, connection) {
        // Use the connection
        var idinput={'User_id':req.body.id,
        'Password':req.body.pa,
        'Email':req.body.email,
        'Phone':req.body.phone,
        'Name':req.body.name,
        'Report_count':0};
        connection.query('Insert into user set ?', idinput, function (err, rows) {
            if (err) console.error("err : " + err);
            console.log("rows : " + JSON.stringify(rows));
            res.redirect('/index.jade');
            connection.release();
            // Don't use the connection here, it has been returned to the pool.
        });
    });


});

module.exports = router;