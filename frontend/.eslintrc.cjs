module.exports = {
  root: true,
  env: { browser: true, es2021: true, node: true },
  extends: ['eslint:recommended'],
  ignorePatterns: ['dist'],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: { jsx: true },
  },
  plugins: ['react-hooks', 'react-refresh'],
  rules: {
    ...require('eslint-plugin-react-hooks').configs.recommended.rules,
    'no-unused-vars': ['error', {
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^[A-Z]',
    }],
    'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
  },
}
