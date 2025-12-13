const path = require("path");
const Dotenv = require("dotenv-webpack");

let config = {
  entry: {
    index: "./frontend/react/index.jsx",
  },

  output: {
    path: path.resolve(__dirname, "backend/static"),
    filename: "[name].bundle.js",
  },

  module: {
    rules: [
      {
        loader: "babel-loader",

        options: {
          presets: ["@babel/preset-react", "@babel/preset-env"],
        },

        exclude: /node_modules/,
      },
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  plugins: [new Dotenv()],
};

module.exports = (env, argv) => {
  if (argv.mode === "development") {
    config.devtool = "inline-source-map";
  }
  return config;
};
