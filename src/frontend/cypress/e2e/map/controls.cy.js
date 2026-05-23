/// <reference types="cypress" />

describe("map-controls", () => {
  beforeEach(() => {
    cy.interceptManifest();
    cy.interceptData();
    cy.visit("/map");
    cy.get("#map").as("map");
  });

  it("has zoom control", () => {
    cy.get("@map")
      .find("div.leaflet-control.leaflet-control-zoom")
      .should("be.visible");
  });

  it("has active control", () => {
    cy.get("@map")
      .find(".leaflet-control.active-container")
      .should("be.visible");
  });

  describe("active control", () => {
    beforeEach(() => {
      cy.get("@map")
        .find(".leaflet-control.active-container")
        .as("active")
        .should("be.visible");
    });

    it("has layout", () => {
      cy.get("@active").find("h2").should("contain.text", "Toggled Overlays");
      cy.get("@active").find("button > span").should("contain.text", "close");
    });

    it("is empty", () => {
      cy.get("@active")
        .find("div.active-body")
        .contains("No toggled overlays")
        .should("be.visible");
    });

    it("can minimise", () => {
      cy.get("@active").find("button").first().click();
      cy.get("@active").find("div.active-body").should("be.hidden");
      cy.get("@active").find(".active-header").should("be.hidden");
      cy.get("@active").find("button").contains("add").click();

      cy.get("@active").find("div.active-body").should("be.visible");
      cy.get("@active").find(".active-header").should("be.visible");
    });

    it("shows active views", () => {
      cy.get("@active").find(".overlay-container").should("have.length", 0);
      cy.get("@active").contains("No toggled overlays");

      cy.get("@map").find("#legendBox.leaflet-control").as("legend");
      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a").contains("plain").click();
      cy.get("@active").find(".overlay-container").should("have.length", 1);

      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a").contains("series").click();
      cy.get("@active").find(".overlay-container").should("have.length", 2);

      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a").contains("plain").click();
      cy.get("@active").find(".overlay-container").should("have.length", 1);

      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a").contains("series").click();
      cy.get("@active").find(".overlay-container").should("have.length", 0);

      cy.get("@active").contains("No toggled overlays");
    });

    it("has buttons for each active view", () => {
      cy.get("@map").find("#legendBox.leaflet-control").as("legend");
      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a").contains("plain").click();

      cy.get("@active")
        .find(".overlay-container .overlay-options")
        .as("options");
      cy.get("@options").find(".show-toggle").should("be.visible");
      cy.get("@options").find(".up-arrow").should("be.visible");
      cy.get("@options").find(".down-arrow").should("be.visible");
    });

    it("allows minimising active views", () => {
      cy.get("@map").find("#legendBox.leaflet-control").as("legend");
      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a").contains("plain").click();

      cy.get("@active")
        .find(".overlay-container .widget-container")
        .should("exist");
      cy.get("@active")
        .find(".overlay-container .overlay-options")
        .as("options");
      cy.get("@options").find(".show-toggle").click();
      cy.get("@active")
        .find(".overlay-container .widget-container")
        .should("not.exist");
      cy.get("@options").find(".show-toggle").click();
      cy.get("@active")
        .find(".overlay-container .widget-container")
        .should("exist");
    });

    it("allows reorganising active views", () => {
      cy.get("@map").find("#legendBox.leaflet-control").as("legend");
      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a").contains("plain").click();
      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a").contains("series").click();

      cy.get("@active")
        .find(".overlay-container .overlay-options")
        .as("options");
      cy.get("@active")
        .find(".overlay-container")
        .eq(1)
        .contains("Group 1 - plain");
      cy.get("@options").eq(0).find(".down-arrow").click();
      cy.get("@active")
        .find(".overlay-container")
        .eq(0)
        .contains("Group 1 - plain");
      cy.get("@options").eq(1).find(".up-arrow").click();
      cy.get("@active")
        .find(".overlay-container")
        .eq(1)
        .contains("Group 1 - plain");
    });
  });

  it("has legend control", () => {
    cy.get("@map").find("#legendBox.leaflet-control").should("be.visible");
  });

  describe("legend control", () => {
    beforeEach(() => {
      cy.get("@map").find("#legendBox.leaflet-control").as("legend");
    });

    it("shows views", () => {
      cy.get("@legend").find(".dropdownMenu").should("not.exist");
      cy.get("@legend").find("button").click();
      cy.get("@legend").find(".dropdownMenu").should("be.visible");
      cy.get("@legend")
        .find(".dropdownMenu .dropdown-item")
        .should("have.length.greaterThan", 0);
      cy.get("@legend").find("button").click();
      cy.get("@legend").find(".dropdownMenu").should("not.be.visible");
    });

    it("toggles views", () => {
      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a").contains("series").click();
      cy.get("@legend")
        .find("a.dropdown-toggled")
        .should("have.length", 1)
        .contains("series");

      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a").contains("values").click();
      cy.get("@legend").find("a.dropdown-toggled").should("have.length", 2);
      cy.get("@legend")
        .find("a.dropdown-toggled")
        .should("have.length", 2)
        .contains("series");
      cy.get("@legend")
        .find("a.dropdown-toggled")
        .should("have.length", 2)
        .contains("values");

      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a").contains("series").click();
      cy.get("@legend")
        .find("a.dropdown-toggled")
        .should("have.length", 1)
        .contains("values");

      cy.get("@legend").find("button").click();
      cy.get("@legend").find("a").contains("values").click();
      cy.get("@legend").find("a.dropdown-toggled").should("have.length", 0);
    });
  });
});
