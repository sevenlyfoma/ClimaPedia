/// <reference types="cypress" />

describe("pie", () => {
  beforeEach(() => {
    cy.interceptManifest();
    cy.interceptData();
    cy.visit("/chart?views=1.pie");
    cy.get(".plot-container").as("pie");
  });

  it("has correct layout", () => {
    cy.get("@pie").find(".slice").should("have.length", 3);
    cy.get("@pie").find(".slice").eq(0).contains("third");
    cy.get("@pie").find(".slice").eq(2).contains("first");
    cy.get("@pie").find(".slice").eq(1).contains("second");
    cy.get("@pie").find(".legendtoggle").should("have.length", 3);
  });

  it("allows toggling series", () => {
    cy.get("@pie").find(".legendtoggle").eq(0).click();
    cy.get("@pie").find(".slice path").should("have.length", 2);
    cy.get("@pie").find(".legendtoggle").eq(1).click();
    cy.get("@pie").find(".slice path").should("have.length", 1);
    cy.get("@pie").find(".legendtoggle").eq(2).click();
    cy.get("@pie").find(".slice path").should("have.length", 0);

    cy.get("@pie").find(".legendtoggle").eq(1).click();
    cy.get("@pie").find(".slice path").should("have.length", 1);
    cy.get("@pie").find(".legendtoggle").eq(2).click();
    cy.get("@pie").find(".slice path").should("have.length", 2);
    cy.get("@pie").find(".legendtoggle").eq(0).click();
    cy.get("@pie").find(".slice path").should("have.length", 3);
  });
});
