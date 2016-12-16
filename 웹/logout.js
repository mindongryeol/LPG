/**
 * Created by USER on 2016-11-28.
 */
var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
    req.session.destroy(function(err){

        res.redirect('/index.jade');
    });
    //res.redirect('/login');
});

module.exports = router;
