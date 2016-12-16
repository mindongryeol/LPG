/**
 * Created by USER on 2016-11-21.
 */
var express = require('express');
var router = express.Router();
var mysql = require('mysql');
var conn = mysql.createConnection({
    connectionLimit: 10,
    host: 'localhost',
    user: 'root',
    database: 'auction',
    password: '32166115'
});

router.get('/buyit/:id',function(req,res,next){
    var io = req.app.get('socketio');
    var curbid_sql = 'SELECT * FROM auction WHERE Auction_id=?;'
    var id = req.params.id;
    var sql ='UPDATE auction set Cur_price=? , Buyer_id=? , Status=? WHERE Auction_id=?;';
    if(req.session.loginId != undefined) {
        conn.query(curbid_sql, [id], function (err, topics) {

                conn.query(sql, [topics[0].Max_price , req.session.loginId,'거래중',id], function (err, rows) {
                    if (err) console.error("err : " + err);
                    console.log("rows : " + JSON.stringify(rows));
                    io.emit('buyitnow_alert');
                    res.redirect('/chatlist');
                });


        });
    }
    else{

        io.emit('login_alert');
        res.redirect('/login');
    }


});


router.get('/add/:id',function(req,res,next){
    var sql = 'SELECT * FROM auction WHERE Status=?;'
    var id = req.params.id;
    conn.query(sql,['입찰대기중'], function(err,topics){
        // for(var i=0; i<topics.length;i++)
        console.log("rows : " + JSON.stringify(topics));
        var sql ='SELECT * FROM auction WHERE Auction_id=? ;'
        conn.query(sql,[id], function(err,rows) {
            if (err) console.error("err : " + err);
            console.log("rows : " + JSON.stringify(rows));

            if (req.session.loginId == null)
                res.render('add', {topics: topics, auctionid: rows[0], login: '로그인'});
            else
                res.render('add', {topics: topics, auctionid: rows[0], login: '로그아웃', userid: JSON.stringify(req.session.name) + '님 안녕하세요'});
        });
    });
});


router.post('/add/:id',function(req,res,next){
    var io = req.app.get('socketio');
    var curbid_sql = 'SELECT * FROM auction WHERE Auction_id=?;'
    var id = req.params.id;
    var sql ='UPDATE auction set Cur_price=? , Buyer_id=? WHERE Auction_id=?;';
     if(req.session.loginId != undefined) {
         conn.query(curbid_sql, [id], function (err, topics) {
             if(topics[0].Cur_price < req.body.current_bid && topics[0].Min_price <= req.body.current_bid  && topics[0].Max_price >= req.body.current_bid ) {
                 conn.query(sql, [req.body.current_bid, req.session.loginId, id], function (err, rows) {
                     if (err) console.error("err : " + err);
                     console.log("rows : " + JSON.stringify(rows));
                     res.redirect('/topic');
                 });
             }
             else if(topics[0].Cur_price >= req.body.current_bid && topics[0].Min_price <= req.body.current_bid  && topics[0].Max_price >= req.body.current_bid ){
                 io.emit('curcost_alert');
                 res.redirect('/topic');
             }
             else if(topics[0].Min_price > req.body.current_bid){
                 io.emit('mincost_alert');
                 res.redirect('/topic');
             }
             else if(topics[0].Max_price < req.body.current_bid){
                 io.emit('maxcost_alert');
                 res.redirect('/topic');
             }
         });
     }
     else{
         var io = req.app.get('socketio');
         io.emit('login_alert');
         res.redirect('/login');
     }

});

router.get('/register', function(req, res, next) {
    var io = req.app.get('socketio');
    if(req.session.loginId != undefined) {
        res.render('topic_register.jade');
    }
    else{
        io.emit('login_alert');
        res.redirect('/login');
    }
});

router.post('/register', function(req, res, next) {

    var sql = 'SELECT * FROM book where title = ?';
    var insert_sql ='INSERT INTO auction (Title,author,publishing, year, Content,Min_price,Max_price,Seller_id,Category,Image_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)';
    var content = req.body.Des;
    var Max_price = req.body.Binp;
    var Min_price = req.body.Mp;
    var Seller = req.session.loginId;
    var select_title = "";
    if(req.body.Category=="All category")
        select_title=req.body.SUB0;
    else if(req.body.Category=="Software")
        select_title=req.body.SUB1;
    else if(req.body.Category=="Media Technology")
        select_title=req.body.SUB2;
    else if(req.body.Category=="Electronics")
        select_title=req.body.SUB3;
    else if(req.body.Category=="Mechanical Engineering")
        select_title=req.body.SUB4;
    else if(req.body.Category=="Mathematics")
        select_title=req.body.SUB5;
    else if(req.body.Category=="Architecture")
        select_title=req.body.SUB6;



        conn.query(sql, select_title, function (err, topics) {
            // for(var i=0; i<topics.length;i++)

            conn.query(insert_sql, [topics[0].title, topics[0].author, topics[0].publishing, topics[0].year, content, Min_price, Max_price, Seller, topics[0].category, topics[0].img_url], function (err, rows) {
                if (err) console.error("err : " + err);

                io.emit('submit_alert');
                res.redirect('/topic');


                // Don't use the connection here, it has been returned to the pool.
            });


        });








});
router.get('/',function(req, res, next) {
    var sql = 'SELECT * FROM auction WHERE Status=?;'
    conn.query(sql,'입찰대기중' ,function (err, topics) {
        // for(var i=0; i<topics.length;i++)
        console.log("rows : " + JSON.stringify(topics));
        console.log("longin id : " + req.session.loginId);
        if (req.session.loginId == null)
            res.render('example', {topics: topics, login: '로그인'});
        else
            res.render('example', {topics: topics, login: '로그아웃', userid: JSON.stringify(req.session.name) + '님 안녕하세요'});
    });

});


router.post('/', function(req,res,next){

   var msg = req.body.search;
    var cate= req.body.city2;


    console.log("Title :"+msg + cate);
    var sql = 'SELECT * FROM auction where Title like "%' + msg + '%"';
    conn.query(sql, function (err, rows) {
        if (err) console.error("err : " + err);
        console.log("rows : " + JSON.stringify(rows));
        if (req.session.loginId == null)
            res.render('example', {topics: rows, login: '로그인'});
        else
            res.render('example', {topics: rows, login: '로그아웃', userid: JSON.stringify(req.session.name) + '님 안녕하세요'});
    });

});

module.exports = router;