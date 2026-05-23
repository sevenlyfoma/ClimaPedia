/// <reference types="cypress" />

describe("point-heat", () => {
  beforeEach(() => {
    cy.interceptManifest();
    cy.interceptData();
    cy.interceptParts();
    cy.visit("/map");
    cy.get("#map").as("map");
    cy.get("@map").find("#legendBox.leaflet-control").as("legend");
    cy.get("@map").find(".leaflet-control.active-container").as("active");

    cy.get("@legend").find("button").click();
    cy.get("@legend").contains("heat").click();
    cy.get("@active").find(".overlay-container").as("overlay");
  });

  it("renders heatmap", () => {
    cy.get("@map")
      .find(".leaflet-3-heat-pane canvas.leaflet-heatmap-layer")
      .should("be.visible");
  });
  it("shows legend", () => {
    cy.get("@overlay")
      .find(".widget")
      .contains("Heat Legend")
      .parent()
      .as("legend1");
    cy.get("@legend1").find(".colour-scale").should("be.visible");
    cy.get("@legend1").find(".colour-ticks p").should("have.length", 5);
  });
});
