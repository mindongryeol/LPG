/**
 * Created by admin on 2016-12-03.
 */
var express = require('express');
var router = express.Router();
//만들어야하는것 --------------

/* GET home page. */
router.get('/', function(req, res, next) {
    if(req.session.loginId ==null)
        res.render('chat', { login: '로그인' });
    else
        res.render('chat', { login: '로그아웃' , userid : JSON.stringify(req.session.name)+'님 안녕하세요'});
});

module.exports = router;
