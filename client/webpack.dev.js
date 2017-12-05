const common = require('./webpack.common.js');
const merge = require('webpack-merge');
const webpack = require('webpack');


module.exports = merge(common, {
    devServer: {
        hot: true,
        publicPath: '/static/dist/'
    },
    plugins: [
        new webpack.NamedModulesPlugin(),
        new webpack.HotModuleReplacementPlugin()
    ]
});
