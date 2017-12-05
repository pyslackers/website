const autoprefixer = require('autoprefixer');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const path = require('path');
const webpack = require('webpack');


module.exports = {
    entry: {
        app: path.resolve(__dirname, 'app.js')
    },
    output: {
        path: path.resolve(__dirname, '../pyslackers_website/static/dist/'),
        filename: '[name].js',
    },
    devtool: 'source-map',
    plugins: [
        new CleanWebpackPlugin(['pyslackers_website/static/dist/'], {
            root: path.resolve(__dirname, '..')
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'commons'
        }),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery'
        }),
        new ExtractTextPlugin("app.css")
    ],
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['env']
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
                use: ExtractTextPlugin.extract({
                    fallback: 'style-loader',
                    use: [
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
                })
            },
            { // Images and Fonts
                test: /\.(png|svg|jpg|gif|woff|woff2|eot|ttf|otf)$/,
                use: ['file-loader']
            }
        ]

    }
};
