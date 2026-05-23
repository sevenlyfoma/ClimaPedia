/// <reference types="cypress" />

describe("page root", () => {
  describe("navbar", () => {
    beforeEach(() => {
      cy.interceptManifest();
      cy.visit("/");
      cy.get("nav.navbar").as("nav");
    });

    it("contains brand", () => {
      cy.get("@nav").find("a.navbar-brand").should("exist");
    });

    it("contains page links", () => {
      cy.get("@nav").find("a.nav-link").eq(0).should("include.text", "Map");
      cy.get("@nav").find("a.nav-link").eq(1).should("include.text", "Chart");
    });

    it("can navigate to links", () => {
      cy.get("@nav").find("a.nav-link").eq(1).click();
      cy.url().should("include", "/chart");
      cy.get("@nav").find("a.nav-link").eq(0).click();
      cy.url().should("not.include", "/chart");
    });

    it("contains settings", () => {
      cy.get("@nav").find("button").last().contains("settings");

      // Settings modal should not be visible until click
      cy.get("div.modal-dialog").should("not.exist");
    });

    describe("settings modal", () => {
      beforeEach(() => {
        cy.get("@nav").find("button").last().click();
        cy.get("div.modal-dialog").as("settings");
      });

      it("has header", () => {
        cy.get("@settings").find("div.modal-header").contains("Settings");
        cy.get("@settings")
          .find("div.modal-header")
          .find('button[aria-label="Close"]')
          .should("exist");
      });

      it("has body", () => {
        // Add more settings here
        cy.get("@settings")
          .find("div.modal-body")
          .contains("Colour Adjustments");
      });

      it("has footer", () => {
        cy.get("@settings")
          .find("div.modal-footer")
          .find("button")
          .as("modal-buttons")
          .eq(0)
          .should("contain.text", "Close");
        cy.get("@modal-buttons").eq(1).should("contain.text", "Save & Close");
      });

      it("can close", () => {
        // Close via header button
        cy.get("@settings")
          .should("exist")
          .find("div.modal-header")
          .find('button[aria-label="Close"]')
          .click();
        cy.get("@settings").should("not.exist");

        // Reopen and close via footer button
        cy.get("@nav").find("button").last().click();
        cy.get("@settings").should("exist");
        cy.get("@settings")
          .find("div.modal-footer")
          .find("button")
          .eq(0)
          .click();
        cy.get("@settings").should("not.exist");
      });
    });
  });
});
