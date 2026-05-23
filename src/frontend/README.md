# Weather Project Frontend

This directory contains the frontend code for the Weather Project.

It is written in React with TypeScript, working in Vite with HMR and some ESLint rules. Prettier has also been installed for formatting.

## Developing

Before developing, run the following command to install the necessary dependencies. Also ensure you node version is at least `16.14.0` or higher.

```sh
npm install
```

### Running

To run the frontend in development mode, execute the following:

```sh
npm run dev
```

This will host a hot-reloading website over localhost, so that you may make changes in the code and see the changes automatically apply.

### Linting and Formatting

Eslint should be configured to provide linting and type checking. VSCode is recommended for development due to its in built TypeScript support, although eslint language servers can also be installed for other editors like Vim.

To manually lint your code, you can run:

```sh
npm run lint
```

To format your code manually with Prettier, you can run:

```sh
npm run format
```

## Testing

To test the frontend, complete the following steps:

1. Ensure you have run `npm install` before hand.
1. Ensure that `FRONTEND_TEST=0` in the `.env` file.
2. Either set `FRONTEND_PORT` to `8081` or change `CYPRESS_BASE_URL` to the url which the frontend will be run on.
3. Run the frontend with `npm run dev`.
4. In a separate terminal, run `npx cypress run` to execute the e2e tests.

## Directory Structure

Here's a basic rundown of the relevant files in the project.

- `node_modules/` contains all the automatically installed JS modules.
- `public/` contains all the static resources. Files placed in this directory are served at the root path `/` by the development server.
- `cypress/` contains the end-to-end tests for the website.
- `src` is where the source code goes.
  - `assets/` is another place to include program assets, to be directly imported in TypeScript code.
  - `main.tsx` is the entry point of the program, it shouldn't need to be changed.
  - `App.tsx` is the entry point component and where the page structure is defined
  - `index.css` is the global CSS file for the website
  - `App.css` is an example of a CSS file for `App.tsx`.
  - `Root.tsx` represents the root component shared between all pages
  - `index/IndexPage.tsx` is the component for the index page (not used)
  - `map/MapPage.tsx` is the component for the map page
  - `chart/ChartPage.tsx` is the component for the chart page
  - `common/` contains components shared between different parts of the website
  - `utils/` contains useful utility functions that may be used between multiple components
  - `utils/api.ts` contains any function calls to the backend api
  - `vite-env.d.ts` is TypeScript type file, don't worry about it.
- `package.json` is like the manifest for our program. In Python terms, it is like the `requirement.txt`.
- `index.html` the HTML boilerplate for the program, should not be modified.

Vite provides a lot of useful functionality, such as for importing assets and CSS directly into TypeScript. For CSS, this allows use to write component-specific CSS. Read more about what Vite offers on their [website](https://vitejs.dev/guide/features.html).

## Environmental Variables

By setting environmental variables in a `.env` file in the root directory of the project, you can change how the frontend is deployed. `example.env` shows all the possible environmental variables you can set, and the ones prefixed with `FRONTEND_` apply to the frontend.

- `FRONTEND_PORT` refers to the port that the frontend development server is run in. Defaults to 5173.
- `FRONTEND_TEST` refers to whether the frontend will read its own test data, or read data from the backend. Defaults to reading from the backend (0), but can be enabled by setting to 1.
- `FRONTEND_API_PATH` refers to the path where frontend will read data from. Will default to the frontend's own URL. If `FRONTEND_TEST` is set to 1, this will not be used.
