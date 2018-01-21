const common = require('./webpack.common.js');
const merge = require('webpack-merge');
const webpack = require('webpack');


module.exports = merge(common, {
  devServer: {
    hot: true,
    publicPath: '/static/dist/',
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'X-Requested-With, content-type, Authorization'
    }
  },
  plugins: [
    new webpack.NamedModulesPlugin(),
    new webpack.HotModuleReplacementPlugin()
  ]
});
