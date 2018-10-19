const CleanWebpackPlugin = require('clean-webpack-plugin');
const common = require('./webpack.common.js');
const merge = require('webpack-merge');
const path = require('path');
const webpack = require('webpack');


module.exports = merge(common, {
  mode: 'production',
  plugins: [
    new CleanWebpackPlugin(['app/static/dist/'], {
      root: path.resolve(__dirname, '..')
    }),
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production')
    })
  ]
});
