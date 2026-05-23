/// <reference types="cypress" />

describe("points", () => {
  beforeEach(() => {
    cy.interceptManifest();
    cy.interceptData();
    cy.interceptParts();
    cy.visit("/map");
    cy.get("#map").as("map");
    cy.get("@map").find("#legendBox.leaflet-control").as("legend");
    cy.get("@map").find(".leaflet-control.active-container").as("active");
  });

  describe("plain", () => {
    beforeEach(() => {
      cy.get("@legend").find("button").click();
      cy.get("@legend").contains("plain").click();
      cy.get("@active").find(".overlay-container").as("overlay");
    });

    it("shows description", () => {
      cy.get("@overlay").find(".widget").contains("Description");
    });

    it("renders points", () => {
      cy.get("@map")
        .find(".leaflet-1-plain-pane path")
        .as("points")
        .should("have.length", 4);
    });
  });

  describe("series", () => {
    beforeEach(() => {
      cy.get("@legend").find("button").click();
      cy.get("@legend").contains("series").click();
      cy.get("@active").find(".overlay-container").as("overlay");
    });

    it("shows legend", () => {
      cy.get("@overlay")
        .find(".widget")
        .contains("Legend")
        .parent()
        .as("legend1");
      cy.get("@legend1").find(".series-field").should("have.length", 3);
      cy.get("@legend1").find(".series-field").eq(0).contains("series 1");
      cy.get("@legend1").find(".series-field").eq(1).contains("series 2");
      cy.get("@legend1").find(".series-field").eq(2).contains("series 3");
    });

    it("filters points", () => {
      cy.get("@overlay").find(".widget .series-field button").as("series");
      cy.get("@map").find(".leaflet-1-series-pane path").as("points");

      // Testing filtering differnet points by different series
      cy.get("@points").should("have.length", 5);
      cy.get("@series").eq(0).click();
      cy.get("@points").should("have.length", 3);
      cy.get("@series").eq(1).click();
      cy.get("@points").should("have.length", 1);
      cy.get("@series").eq(0).click();
      cy.get("@points").should("have.length", 3);
      cy.get("@series").eq(2).click();
      cy.get("@points").should("have.length", 2);
      cy.get("@series").eq(0).click();
      cy.get("@points").should("have.length", 0);
      cy.get("@series").eq(0).click();
      cy.get("@points").should("have.length", 2);
      cy.get("@series").eq(1).click();
      cy.get("@points").should("have.length", 4);
      cy.get("@series").eq(2).click();
      cy.get("@points").should("have.length", 5);
    });
  });

  describe("values", () => {
    beforeEach(() => {
      cy.get("@legend").find("button").click();
      cy.get("@legend").contains("values").click();
      cy.get("@active").find(".overlay-container").as("overlay");
    });

    it("renders points", () => {
      cy.get("@map")
        .find(".leaflet-2-values-pane path")
        .should("have.length", 4);
    });

    it("shows legend", () => {
      cy.get("@overlay")
        .find(".widget")
        .contains("Legend")
        .parent()
        .as("legend1");
      cy.get("@legend1").find(".colour-scale").should("be.visible");
      cy.get("@legend1").find(".colour-ticks p").should("have.length", 5);
      cy.get("@legend1")
        .find(".colour-ticks p")
        .eq(0)
        .should("have.text", "10.0 mm");
      cy.get("@legend1")
        .find(".colour-ticks p")
        .eq(4)
        .should("have.text", "-10.0 mm");
    });
  });

  describe("click", () => {
    beforeEach(() => {
      cy.get("@legend").find("button").click();
      cy.get("@legend").contains("click").click();
      cy.get("@active").find(".overlay-container").as("overlay");
    });

    it("supports clicking", () => {
      cy.get("@map")
        .find(".leaflet-2-click-pane path")
        .as("points")
        .should("have.length", 3);

      // Should not be toggled
      cy.get("@points").eq(0).should("have.attr", "stroke-width", "1");

      // Click first point
      cy.get("@points").eq(0).click();

      // Should be toggled
      cy.get("@points").eq(0).should("have.attr", "stroke-width", "3");

      cy.get("@overlay")
        .contains("point 1")
        .parent()
        .find(".custom-content")
        .as("custom");
      cy.get("@custom")
        .find("h1")
        .should("have.text", "apple")
        .and("be.visible");
      cy.get("@custom")
        .find("img")
        .should(
          "have.attr",
          "src",
          "https://www.st-andrews.ac.uk/assets/university/brand/logos/standard-vertical-black.png",
        )
        .and("be.visible");
      cy.get("@custom").parent().should("have.class", "small-widget");

      // Click first point again
      cy.get("@points").eq(0).click();
      cy.get("@overlay").contains("point 1").should("not.exist");
      cy.get("@points").eq(0).should("have.attr", "stroke-width", "1");

      // Click second point
      cy.get("@points").eq(1).should("have.attr", "stroke-width", "1");
      cy.get("@points").eq(1).click();
      cy.get("@points").eq(1).should("have.attr", "stroke-width", "3");
      cy.get("@overlay")
        .contains("point 2")
        .parent()
        .find(".custom-content")
        .as("custom");
      cy.get("@custom")
        .find("h2")
        .should("have.text", "bear")
        .and("be.visible");
      cy.get("@custom").find("p").should("have.text", "food").and("be.visible");
      cy.get("@custom").parent().should("have.class", "large-widget");

      // Click third point
      cy.get("@points").eq(2).click();
      cy.get("@points").eq(2).should("have.attr", "stroke-width", "3");
      cy.get("@points").eq(1).should("have.attr", "stroke-width", "1");
      cy.get("@overlay").contains("point 2").should("not.exist");
      cy.get("@overlay")
        .contains("point 3")
        .parent()
        .find(".custom-content")
        .as("custom");
      cy.get("@custom")
        .find("p")
        .should("have.text", "daylight")
        .and("be.visible");
      cy.get("@custom").parent().should("have.class", "large-widget");
    });
  });

  describe("clustering", () => {
    beforeEach(() => {
      cy.get("@legend").find("button").click();
      cy.get("@legend").contains("cluster").click();
      cy.get("@active").find(".overlay-container").as("overlay");
    });

    it("renders clusters", () => {
      // Only one visible point currently, rest clustered
      cy.get("@map")
        .find(".leaflet-2-cluster-pane path")
        .as("points")
        .should("have.length", 1);

      // Two clusters
      cy.get("@map")
        .find(".leaflet-2-cluster-pane .marker-cluster")
        .as("clusters")
        .should("have.length", 2);
      cy.get("@clusters").contains("7");
      cy.get("@clusters").contains("2");
    });

    it("clusters more on zoom out", () => {
      cy.get("@map").find(".leaflet-2-cluster-pane path").as("points");
      cy.get("@map")
        .find(".leaflet-2-cluster-pane .marker-cluster")
        .as("clusters");

      cy.get(".leaflet-control-zoom-out").click();

      // Point gets absorbed by marker
      cy.get("@points").should("have.length", 0);
      cy.get("@clusters").should("have.length", 2);
      cy.get("@clusters").contains("2");
      cy.get("@clusters").contains("8");

      cy.get(".leaflet-control-zoom-out").click();

      // Markers combine into single bigger marker
      cy.get("@points").should("have.length", 0);
      cy.get("@clusters").should("have.length", 1);
      cy.get("@clusters").contains("10");
    });
    it("clusters less on zoom in", () => {
      cy.get("@map").find(".leaflet-2-cluster-pane path").as("points");
      cy.get("@map")
        .find(".leaflet-2-cluster-pane .marker-cluster")
        .as("clusters");

      cy.get(".leaflet-control-zoom-in").click();

      // Markers get smaller
      cy.get("@points").should("have.length", 3);
      cy.get("@clusters").should("have.length", 2);
      cy.get("@clusters").contains("3");
      cy.get("@clusters").contains("4");
    });
    it("zooms in on cluster click", () => {
      cy.get("@map").find(".leaflet-2-cluster-pane path").as("points");
      cy.get("@map")
        .find(".leaflet-2-cluster-pane .marker-cluster")
        .as("clusters");

      // Zooms in until only a single marker left
      cy.get("@clusters").eq(1).click();

      cy.get("@points").should("have.length", 8);
      cy.get("@clusters").should("have.length", 1);
      cy.get("@clusters").contains("2");
    });
    it("supports clicking points", () => {
      cy.get("@map").find(".leaflet-2-cluster-pane path").as("points");
      cy.get("@map")
        .find(".leaflet-2-cluster-pane .marker-cluster")
        .as("clusters");

      cy.get("@clusters").eq(1).click();
      cy.get("@points").eq(6).should("have.attr", "stroke-width", "1");
      cy.get("@points").eq(6).click();
      cy.get("@points").eq(6).should("have.attr", "stroke-width", "3");
      cy.get("@overlay")
        .contains("point 4")
        .parent()
        .find(".custom-content")
        .as("custom");
      cy.get("@custom")
        .find("p")
        .should("have.text", "sunset")
        .and("be.visible");
      cy.get("@points").eq(6).click();
      cy.get("@points").eq(6).should("have.attr", "stroke-width", "1");
    });

    it("supports series", () => {
      cy.get("@legend").find("button").click();
      cy.get("@legend").contains("cluster").click();
      cy.get("@legend").find("button").click();
      cy.get("@legend").contains("cluster-series").click();

      cy.get("@map").find(".leaflet-2-cluster-series-pane path").as("points");
      cy.get("@map")
        .find(".leaflet-2-cluster-series-pane .marker-cluster")
        .as("clusters");

      cy.get("@overlay").find(".widget .series-field button").as("series");

      cy.get("@points").should("have.length", 1);
      cy.get("@clusters").should("have.length", 2);
      cy.get("@clusters").contains("7");
      cy.get("@clusters").contains("2");
      cy.get("@series").eq(0).click();

      cy.get("@points").should("have.length", 0);
      cy.get("@clusters").should("have.length", 2);
      cy.get("@clusters").contains("5");
      cy.get("@clusters").contains("2");

      cy.get("@series").eq(0).click();
      cy.get("@points").should("have.length", 1);
      cy.get("@clusters").should("have.length", 2);
      cy.get("@clusters").contains("7");
      cy.get("@clusters").contains("2");

      cy.get("@series").eq(1).click();
      cy.get("@points").should("have.length", 2);
      cy.get("@clusters").should("have.length", 1);
      cy.get("@clusters").contains("6");

      cy.get("@series").eq(2).click();
      cy.get("@points").should("have.length", 1);
      cy.get("@clusters").should("have.length", 1);
      cy.get("@clusters").contains("2");

      cy.get("@series").eq(0).click();
      cy.get("@points").should("have.length", 0);
      cy.get("@clusters").should("have.length", 0);

      cy.get("@series").eq(1).click();
      cy.get("@points").should("have.length", 2);
      cy.get("@clusters").should("have.length", 0);

      cy.get("@series").eq(0).click();
      cy.get("@points").should("have.length", 2);
      cy.get("@clusters").should("have.length", 1);
      cy.get("@clusters").contains("3");

      cy.get("@series").eq(2).click();
      cy.get("@points").should("have.length", 1);
      cy.get("@clusters").should("have.length", 2);
      cy.get("@clusters").contains("7");
      cy.get("@clusters").contains("2");
    });
  });
});
