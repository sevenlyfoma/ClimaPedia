/// <reference types="cypress" />

describe("point-trees", () => {
  beforeEach(() => {
    cy.interceptManifest();
    cy.interceptData();
    cy.interceptParts();
    cy.visit("/map");
    cy.get("#map").as("map");
    cy.get("@map").find("#legendBox.leaflet-control").as("legend");
    cy.get("@map").find(".leaflet-control.active-container").as("active");

    cy.get("@legend").find("button").click();
    cy.get("@legend").contains("tree").click();
    cy.get("@active").find(".overlay-container").as("overlay");
  });

  it("shows root points", () => {
    cy.get("@map").find(".leaflet-3-tree-pane path").as("points");
    cy.get("@points").should("have.length", 2);
  });

  it("can expand point", () => {
    cy.get("@map").find(".leaflet-3-tree-pane path").as("points");
    cy.get("@points").eq(0).click();
    cy.get("@points").should("have.length", 3);
    cy.get("@map").find(".leaflet-line-pane path").as("lines");
    cy.get("@lines").should("have.length", 1);
    cy.get("@points").eq(1).click();
    cy.get("@lines").should("have.length", 3);
    cy.get("@points").should("have.length", 5);
    cy.get("@points").eq(0).click();
    cy.get("@lines").should("have.length", 2);
    cy.get("@points").should("have.length", 4);

    cy.get("@points").eq(2).click();
    cy.get("@lines").should("have.length", 5);
    cy.get("@points").should("have.length", 7);
  });

  it("closes all descendants on ancestor close", () => {
    cy.get("@map").find(".leaflet-3-tree-pane path").as("points");
    cy.get("@points").eq(1).click();
    cy.get("@points").eq(2).click();
    cy.get("@map").find(".leaflet-line-pane path").as("lines");
    cy.get("@lines").should("have.length", 5);
    cy.get("@points").should("have.length", 7);
    cy.get("@points").eq(1).click();
    cy.get("@lines").should("have.length", 0);
    cy.get("@points").should("have.length", 2);
  });

  it("supports showing custom content", () => {
    cy.get("@map").find(".leaflet-3-tree-pane path").as("points");

    cy.get("@points").eq(0).should("have.attr", "stroke-width", "1");
    cy.get("@points").eq(0).click();
    cy.get("@points").eq(0).should("have.attr", "stroke-width", "3");

    cy.get("@overlay")
      .contains("point 1")
      .parent()
      .find(".custom-content")
      .as("custom");
    cy.get("@custom").find("p").should("have.text", "Sofia").and("be.visible");

    // point at eq(1) has no custom content, so don't change toggle
    cy.get("@points").eq(1).click();
    cy.get("@points").eq(0).should("have.attr", "stroke-width", "3");
    cy.get("@points").eq(1).should("have.attr", "stroke-width", "1");

    // point at eq(3) has no custom content, so don't change toggle
    cy.get("@points").eq(3).click();
    cy.get("@points").eq(0).should("have.attr", "stroke-width", "3");
    cy.get("@points").eq(3).should("have.attr", "stroke-width", "1");

    // This point does have custom content
    cy.get("@points").eq(5).click();

    cy.get("@overlay")
      .contains("point 6")
      .parent()
      .find(".custom-content")
      .as("custom");
    cy.get("@custom").find("p").should("have.text", "Adele").and("be.visible");

    cy.get("@points").eq(0).should("have.attr", "stroke-width", "1");
    cy.get("@points").eq(5).should("have.attr", "stroke-width", "3");

    cy.get("@points").eq(1).click();

    cy.get("@overlay").find(".title").should("not.contain.text", "point 6");
  });

  it("supports series filtering", () => {
    cy.get("@map").find(".leaflet-3-tree-pane path").as("points");
    cy.get("@overlay").find(".widget .series-field button").as("series");
    cy.get("@points").eq(1).click();
    cy.get("@points").eq(2).click();

    cy.get("@points").should("have.length", 7);
    cy.get("@series").eq(0).click();
    cy.get("@points").should("have.length", 4);
    cy.get("@map").find(".leaflet-inactive-pane path").as("inactive");
    cy.get("@inactive").should("have.length", 3);

    cy.get("@series").eq(1).click();
    cy.get("@inactive").should("have.length", 7);
    cy.get("@points").should("have.length", 0);

    cy.get("@series").eq(0).click();
    cy.get("@inactive").should("have.length", 4);
    cy.get("@points").should("have.length", 3);

    cy.get("@series").eq(1).click();
    cy.get("@inactive").should("have.length", 0);
    cy.get("@points").should("have.length", 7);
  });
});
