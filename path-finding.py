from enum import Enum
from typing import Optional
from collections import namedtuple
import pprint

import arcade

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 32
SCREEN_TITLE = "Path Finding"

NodeType = Enum("NodeType", ["FREE", "EXPLORED", "WALL", "GRASS", "START", "TARGET"])
Point = namedtuple("Point", "x y")

START_NODE_COORDINATES = Point(12, 4)
TARGET_NODE_COORDINATES = Point(10, 4)


class Node(arcade.SpriteSolidColor):
    def __init__(
        self,
        color: arcade.Color,
        center_x: float,
        center_y: float,
        node_type: NodeType,
        previous_node: Optional["Node"],
    ):
        super().__init__(GRID_SIZE, GRID_SIZE, color)
        self.center_x = center_x
        self.center_y = center_y
        self.node_type = node_type
        self.previous_node = previous_node


class PathFinding(arcade.Window):
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)
        self.nodes = self.get_nodes()
        self.search_for_path = True

    def get_nodes(self) -> list[list[Node]]:
        nodes = []
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            row = arcade.SpriteList()
            for x in range(0, SCREEN_WIDTH, GRID_SIZE):
                row.append(
                    Node(
                        arcade.color.BLACK,
                        x + GRID_SIZE / 2,
                        y + GRID_SIZE / 2,
                        NodeType.FREE,
                        None,
                    )
                )
            nodes.append(row)
        nodes[START_NODE_COORDINATES.y][
            START_NODE_COORDINATES.x
        ].node_type = NodeType.START
        nodes[TARGET_NODE_COORDINATES.y][
            TARGET_NODE_COORDINATES.x
        ].node_type = NodeType.TARGET
        return nodes

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.SPACE:
            self.breadth_first_search()

    def breadth_first_search(self) -> None:
        coordinates_to_visit = []
        coordinates_to_visit.append(START_NODE_COORDINATES)
        while coordinates_to_visit:
            current_node_coordinates = coordinates_to_visit.pop(0)
            if current_node_coordinates == TARGET_NODE_COORDINATES:
                self.search_for_path = False
                break
            if self.can_visit_left_node(current_node_coordinates):
                coordinates_to_visit.append(
                    Point(current_node_coordinates.x - 1, current_node_coordinates.y)
                )
                self.nodes[current_node_coordinates.y][
                    current_node_coordinates.x - 1
                ].node_type = NodeType.EXPLORED
                self.nodes[current_node_coordinates.y][
                    current_node_coordinates.x - 1
                ].previous_node = self.nodes[current_node_coordinates.y][
                    current_node_coordinates.x
                ]
            if self.can_visit_right_node(current_node_coordinates):
                coordinates_to_visit.append(
                    Point(current_node_coordinates.x + 1, current_node_coordinates.y)
                )
                self.nodes[current_node_coordinates.y][
                    current_node_coordinates.x + 1
                ].node_type = NodeType.EXPLORED
                self.nodes[current_node_coordinates.y][
                    current_node_coordinates.x + 1
                ].previous_node = self.nodes[current_node_coordinates.y][
                    current_node_coordinates.x
                ]
            if self.can_visit_bottom_node(current_node_coordinates):
                coordinates_to_visit.append(
                    Point(current_node_coordinates.x, current_node_coordinates.y - 1)
                )
                self.nodes[current_node_coordinates.y - 1][
                    current_node_coordinates.x
                ].node_type = NodeType.EXPLORED
                self.nodes[current_node_coordinates.y - 1][
                    current_node_coordinates.x
                ].previous_node = self.nodes[current_node_coordinates.y][
                    current_node_coordinates.x
                ]
            if self.can_visit_top_node(current_node_coordinates):
                coordinates_to_visit.append(
                    Point(current_node_coordinates.x, current_node_coordinates.y + 1)
                )
                self.nodes[current_node_coordinates.y + 1][
                    current_node_coordinates.x
                ].node_type = NodeType.EXPLORED
                self.nodes[current_node_coordinates.y + 1][
                    current_node_coordinates.x
                ].previous_node = self.nodes[current_node_coordinates.y][
                    current_node_coordinates.x
                ]

    def can_visit_left_node(self, current_node_coordinates: Point) -> bool:
        return current_node_coordinates.x != 0 and self.nodes[
            current_node_coordinates.y
        ][current_node_coordinates.x - 1].node_type not in {
            NodeType.EXPLORED,
            NodeType.START,
        }

    def can_visit_right_node(self, current_node_coordinates: Point) -> bool:
        return current_node_coordinates.x != len(
            self.nodes[current_node_coordinates.y]
        ) - 1 and self.nodes[current_node_coordinates.y][
            current_node_coordinates.x + 1
        ].node_type not in {
            NodeType.EXPLORED,
            NodeType.START,
        }

    def can_visit_bottom_node(self, current_node_coordinates: Point) -> bool:
        return current_node_coordinates.y != 0 and self.nodes[
            current_node_coordinates.y - 1
        ][current_node_coordinates.x].node_type not in {
            NodeType.EXPLORED,
            NodeType.START,
        }

    def can_visit_top_node(self, current_node_coordinates: Point) -> bool:
        return current_node_coordinates.y != len(self.nodes) - 1 and self.nodes[
            current_node_coordinates.y + 1
        ][current_node_coordinates.x].node_type not in {
            NodeType.EXPLORED,
            NodeType.START,
        }

    def on_draw(self) -> None:
        self.clear()
        self.draw_nodes()
        self.draw_grid()

    def draw_nodes(self) -> None:
        for row in self.nodes:
            for node in row:
                match node.node_type:
                    case NodeType.EXPLORED:
                        arcade.draw_rectangle_filled(
                            node.center_x,
                            node.center_y,
                            GRID_SIZE,
                            GRID_SIZE,
                            arcade.color.BLUE,
                        )
                    case NodeType.START:
                        arcade.draw_rectangle_filled(
                            node.center_x,
                            node.center_y,
                            GRID_SIZE,
                            GRID_SIZE,
                            arcade.color.GREEN,
                        )
                    case NodeType.TARGET:
                        arcade.draw_rectangle_filled(
                            node.center_x,
                            node.center_y,
                            GRID_SIZE,
                            GRID_SIZE,
                            arcade.color.YELLOW,
                        )

    def draw_grid(self) -> None:
        for row in self.nodes:
            for node in row:
                arcade.draw_rectangle_outline(
                    node.center_x,
                    node.center_y,
                    GRID_SIZE,
                    GRID_SIZE,
                    arcade.color.WHITE,
                    border_width=4,
                )


def main() -> None:
    PathFinding(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
