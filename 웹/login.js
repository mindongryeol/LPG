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

/*app.io = io.sockets.on('connection',function(socket){
    socket.emit('alert');
});*/

router.get('/',function(req, res, next) {

    res.render('login');
});

router.post('/',function(req, res, next) {
    pool.getConnection(function (err, connection) {
        connection.query('SELECT * FROM user WHERE User_id = ?', req.body.id, function (err, rows) {
            if (err) console.error("err : " + err);
            console.log("rows : " + JSON.stringify(rows[0]));
            //onsole.log(JSON.stringify(rows[0].Password));
            if(rows.length != 0) {
                if (rows[0].Password  == req.body.pa) {
                    console.log('true');
                    req.session.loginId=rows[0].User_id;
                    req.session.name=rows[0].Name;
                    req.session.email=rows[0].Email;
                    req.session.phone=rows[0].Phone;
                    console.log(req.session.loginId);
                    req.session.save();

                    res.redirect('/index.jade');

                }
                else {
                    console.log('false');
                    var io = req.app.get('socketio');
                    io.emit('alert');
                    res.redirect('/login');
                }
            }
            else{
                var io = req.app.get('socketio');
                io.emit('alert');
               res.redirect('/');
            }
            connection.release();
            //res.redirect('/login');
            // Don't use the connection here, it has been returned to the pool.
        });
    });

});



module.exports = router;