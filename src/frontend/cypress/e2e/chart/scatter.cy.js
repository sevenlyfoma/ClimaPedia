/// <reference types="cypress" />

describe("scatter", () => {
  beforeEach(() => {
    cy.interceptManifest();
    cy.interceptData();
    cy.interceptParts();
    cy.visit("/chart?views=4.scatter");
    cy.get(".plot-container").as("scatter");
  });

  it("has correct layout", () => {
    cy.get("@scatter").find(".point").should("have.length", 4);

    // No legend if none needed
    cy.get("@scatter").find(".legendtoggle").should("have.length", 0);
  });

  describe("scatter-series", () => {
    beforeEach(() => {
      cy.visit("/chart?views=4.scatter-series");
    });

    it("has correct layout", () => {
      cy.get("@scatter").find(".point").should("have.length", 4);
      cy.get("@scatter").find(".legendtoggle").should("have.length", 2);
    });

    it("allows toggling series", () => {
      cy.get("@scatter").find(".legendtoggle").eq(0).click();
      cy.get("@scatter").find(".point").should("have.length", 2);

      cy.get("@scatter").find(".legendtoggle").eq(1).click();
      cy.get("@scatter").find(".point").should("have.length", 0);

      cy.get("@scatter").find(".legendtoggle").eq(0).click();
      cy.get("@scatter").find(".point").should("have.length", 2);

      cy.get("@scatter").find(".legendtoggle").eq(1).click();
      cy.get("@scatter").find(".point").should("have.length", 4);
    });
  });
  describe("scatter-value", () => {
    beforeEach(() => {
      cy.visit("/chart?views=4.scatter-values");
    });

    it("has correct layout", () => {
      cy.get("@scatter").find(".point").should("have.length", 4);
      cy.get("@scatter").find(".legendtoggle").should("have.length", 0);
      cy.get("@scatter").find(".cbbg").should("be.be.visible");
    });
  });
});
