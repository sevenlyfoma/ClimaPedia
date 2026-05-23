/// <reference types="cypress" />
// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//
// declare global {
//   namespace Cypress {
//     interface Chainable {
//       login(email: string, password: string): Chainable<void>
//       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
//     }
//   }
// }

export {};

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace Cypress {
    interface Chainable {
      interceptManifest(): Chainable<void>;
      interceptData(): Chainable<void>;
      interceptParts(): Chainable<void>;
    }
  }
}

Cypress.Commands.add("interceptManifest", () => {
  cy.intercept("GET", "**/api/groups", {
    fixture: "manifest.json",
  });
});

Cypress.Commands.add("interceptData", () => {
  cy.intercept("GET", "**/api/data/*/*", (req) => {
    const data = req.url.slice(req.url.indexOf("/api/data/") + 1).split("/");
    const group = data[2];
    const view = data[3];

    req.reply({
      fixture: `data/${group}.${view}.json`,
    });
  });
});

Cypress.Commands.add("interceptParts", () => {
  cy.intercept("GET", "**/api/data/*/*/*", (req) => {
    const data = req.url.slice(req.url.indexOf("/api/data/") + 1).split("/");
    const group = data[2];
    const view = data[3];
    const id = data[4];

    if (req.url.includes("?")) {
      const params = req.url.split("?")[1];
      req.reply({
        fixture: `part/${group}.${view}.${id.split("?")[0]}.${params}.json`,
      });
      return;
    }

    req.reply({
      fixture: `part/${group}.${view}.${id}.json`,
    });
  });
});
