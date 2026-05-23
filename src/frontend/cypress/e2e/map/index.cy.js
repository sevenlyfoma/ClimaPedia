/// <reference types="cypress" />

describe("map", () => {
  beforeEach(() => {
    cy.interceptManifest();
    cy.interceptData();
    cy.visit("/map");
  });

  it("contains map", () => {
    cy.get("#map").should("not.be.hidden");
  });

  it("is active", () => {
    cy.get("nav")
      .find("a.nav-link")
      .should("contain.text", "Map")
      .should("have.class", "active");
  });

  describe("query parameters", () => {
    beforeEach(() => {
      cy.get("#legendBox.leaflet-control").as("legend");
    });
    it("loads a view", () => {
      cy.get("@legend").find("button").click();
      cy.get("@legend")
        .find("a.dropdown-item.dropdown-toggled")
        .should("have.length", 0);

      cy.visit("/?views=1.series");
      cy.get("@legend").find("button").click();
      cy.get("@legend")
        .find("a.dropdown-item.dropdown-toggled")
        .should("have.text", "series");

      cy.visit("/?views=2.values");
      cy.get("@legend").find("button").click();
      cy.get("@legend")
        .find("a.dropdown-item.dropdown-toggled")
        .should("have.text", "values");
    });

    it("load multiple views", () => {
      cy.visit("/?views=1.plain,1.series");
      cy.get("@legend").find("button").click();
      cy.get("@legend")
        .find("a.dropdown-item.dropdown-toggled")
        .contains("plain");
      cy.get("@legend")
        .find("a.dropdown-item.dropdown-toggled")
        .contains("series");
    });

    it("updates with views", () => {
      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a.dropdown-item").contains("click").click();

      cy.location().should((loc) => {
        expect(loc.search).to.eq("?views=2.click");
      });

      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a.dropdown-item").contains("plain").click();

      cy.location().should((loc) => {
        expect(loc.search).to.eq("?views=1.plain%2C2.click");
      });

      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a.dropdown-item").contains("click").click();

      cy.location().should((loc) => {
        expect(loc.search).to.eq("?views=1.plain");
      });

      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a.dropdown-item").contains("plain").click();

      cy.location().should((loc) => {
        expect(loc.search).to.eq("?views=");
      });
    });
  });
});
