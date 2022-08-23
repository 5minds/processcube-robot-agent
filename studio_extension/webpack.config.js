const path = require('path');

// TODO: add production build
const MODE = 'development';

const config = {
  mode: MODE,
  entry: './index.ts',
  output: {
    libraryTarget: 'commonjs2',
    filename: 'index.js',
    path: path.resolve(__dirname, 'out'),
    publicPath: 'out/',
  },
  resolve: { extensions: ['.ts', '.tsx', '.js'] },
  module: {
    rules: [
      {
        test: /\.(bpmn|txt)$/,
        use: 'raw-loader',
      },
      {
        test: /\.s[ac]ss$/i,
        use: ['style-loader', 'css-loader', 'sass-loader'],
      },
      {
        test: /\.(md|markdown)$/,
        use: 'markdown-image-loader',
      },
      // Webpack tries to compile all files it sees to ensure dynamic imports work.
      // We want to exclude some files, which we definitely won't import dynamically.
      {
        test: [/\.(d|test)\.tsx?$/],
        loader: 'null-loader',
      },
      {
        test: /\.tsx?$/,
        exclude: /\.(d|test)\.tsx?$/,
        loader: 'ts-loader',
        options: { configFile: 'tsconfig.json' },
      },
    ],
  },
  devtool: 'source-map',
  target: 'electron-renderer',
};

module.exports = [config];
