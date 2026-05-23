/// <reference types="cypress" />

describe("line", () => {
  beforeEach(() => {
    cy.interceptManifest();
    cy.interceptData();
    cy.visit("/chart?views=4.line");
    cy.get(".plot-container").as("line");
  });

  it("has correct layout", () => {
    cy.get("@line").find(".trace.scatter").should("have.length", 2);
    cy.get("@line").find(".legendtoggle").should("have.length", 2);
  });

  it("allows toggling series", () => {
    cy.get("@line").find(".legendtoggle").eq(0).click();
    cy.get("@line").find(".trace.scatter").should("have.length", 1);
    cy.get("@line").find(".legendtoggle").eq(1).click();
    cy.get("@line").find(".trace.scatter").should("have.length", 0);
    cy.get("@line").find(".legendtoggle").eq(0).click();
    cy.get("@line").find(".trace.scatter").should("have.length", 1);
    cy.get("@line").find(".legendtoggle").eq(1).click();
    cy.get("@line").find(".trace.scatter").should("have.length", 2);
  });
});
