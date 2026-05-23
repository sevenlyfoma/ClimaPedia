/// <reference types="cypress" />

describe("voronoi-heat", () => {
  beforeEach(() => {
    cy.interceptManifest();
    cy.interceptData();
    cy.interceptParts();
    cy.visit("/map");
    cy.get("#map").as("map");
    cy.get("@map").find("#legendBox.leaflet-control").as("legend");
    cy.get("@map").find(".leaflet-control.active-container").as("active");

    cy.get("@legend").find("button").click();
    cy.get("@legend").contains("voronoi").click();
    cy.get("@active").find(".overlay-container").as("overlay");
  });

  it("renders polygons", () => {
    cy.get("@map")
      .find(".leaflet-3-voronoi-pane path")
      .as("parts")
      .should("have.length", 3);
  });
  it("shows legend", () => {
    cy.get("@overlay")
      .find(".widget")
      .contains("Heat Legend")
      .parent()
      .as("legend1");
    cy.get("@legend1").find(".colour-scale").should("be.visible");
    cy.get("@legend1").find(".colour-ticks p").should("have.length", 4);
  });

  it("supports clicking", () => {
    cy.get("@map").find(".leaflet-3-voronoi-pane path").as("parts");

    cy.get("@parts").eq(0).should("have.attr", "stroke-width", 2);
    cy.get("@parts").eq(0).click();
    cy.get("@parts").eq(0).should("have.attr", "stroke-width", 4);
    cy.get("@overlay")
      .contains("part 0")
      .parent()
      .find(".custom-content")
      .as("custom");
    cy.get("@custom").find("p").should("have.text", "of").and("be.visible");

    cy.get("@parts").eq(1).should("have.attr", "stroke-width", 2);
    cy.get("@parts").eq(1).click();
    cy.get("@parts").eq(1).should("have.attr", "stroke-width", 4);
    cy.get("@parts").eq(0).should("have.attr", "stroke-width", 2);
    cy.get("@overlay")
      .contains("part 1")
      .parent()
      .find(".custom-content")
      .as("custom");
    cy.get("@custom").find("p").should("have.text", "a").and("be.visible");

    cy.get("@parts").eq(2).should("have.attr", "stroke-width", 2);
    cy.get("@parts").eq(2).click();
    cy.get("@parts").eq(2).should("have.attr", "stroke-width", 4);
    cy.get("@parts").eq(1).should("have.attr", "stroke-width", 2);
    cy.get("@overlay")
      .contains("part 2")
      .parent()
      .find(".custom-content")
      .as("custom");
    cy.get("@custom").find("p").should("have.text", "lady").and("be.visible");

    cy.get("@parts").eq(2).click();
    cy.get("@parts").eq(2).should("have.attr", "stroke-width", 2);
  });
});
