const autoprefixer = require('autoprefixer');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const path = require('path');
const webpack = require('webpack');


module.exports = {
  entry: {
    app: path.resolve(__dirname, 'app.js'),
    slack: path.resolve(__dirname, 'slack/slack.js')
  },
  output: {
    path: path.resolve(__dirname, '../app/static/dist/'),
    filename: '[name].js',
  },
  devtool: 'source-map',
  plugins: [
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery'
    }),
    new MiniCssExtractPlugin('app.css')
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['es2017', 'react'],
            plugins: [
              'transform-class-properties',
              'transform-runtime',
              'transform-es2015-arrow-functions',
            ]
          }
        }
      },
      {
        test: /\.css$/,
        use: [
          'style-loader',
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              plugins: () => [autoprefixer]
            }
          }
        ]
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: { minimize: true }
          },
          {
            loader: 'postcss-loader',
            options: {
              plugins: () => [autoprefixer]
            }
          },
          'sass-loader'
        ]
      },
      { // Images and Fonts
        test: /\.(png|svg|jpg|gif|woff|woff2|eot|ttf|otf)$/,
        use: ['file-loader']
      }
    ]
  },
  optimization: {
    splitChunks: {
      name: 'commons',
      chunks: 'initial',
      minChunks: 2
    }
  }
};
