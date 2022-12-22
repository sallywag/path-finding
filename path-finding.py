# refactor mouse motion and press

from enum import Enum
from typing import Optional
from collections import namedtuple
import pprint

import arcade

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 32
SCREEN_TITLE = "Path Finding"

NodeType = Enum(
    "NodeType", ["FREE", "EXPLORED", "WALL", "GRASS", "START", "TARGET", "PATH"]
)
Coordinate = namedtuple("Coordinate", "x y")


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
        self.start_node_coordinates = Coordinate(0, 3)
        self.target_node_coordinates = Coordinate(0, 5)
        self.get_nodes()
        self.search_for_path = True
        self.current_node_coordinates: Coordinate | None = None
        self.coordinates_to_visit: list[Coordinate] = []
        self.node_placement_type = NodeType.WALL
        self.engaged_node: Node | None = None

    def get_nodes(self) -> None:
        self.nodes = []
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
            self.nodes.append(row)
        self.nodes[self.start_node_coordinates.y][
            self.start_node_coordinates.x
        ].node_type = NodeType.START
        self.nodes[self.target_node_coordinates.y][
            self.target_node_coordinates.x
        ].node_type = NodeType.TARGET

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.SPACE:
                if self.search_for_path:
                    self.breadth_first_search()
            case arcade.key.C:
                self.clear_path()
            case arcade.key.W:
                self.node_placement_type = NodeType.WALL
            case arcade.key.S:
                self.node_placement_type = NodeType.START
            case arcade.key.T:
                self.node_placement_type = NodeType.TARGET

    def breadth_first_search(self) -> None:
        self.coordinates_to_visit.append(self.start_node_coordinates)
        while self.coordinates_to_visit:
            self.current_node_coordinates = self.coordinates_to_visit.pop(0)
            if self.current_node_coordinates == self.target_node_coordinates:
                self.nodes[self.current_node_coordinates.y][
                    self.current_node_coordinates.x
                ].node_type = NodeType.TARGET
                self.search_for_path = False
                self.get_path()
                break
            if self.can_visit_left_node():
                self.visit_left_node()
            if self.can_visit_right_node():
                self.visit_right_node()
            if self.can_visit_bottom_node():
                self.visit_bottom_node()
            if self.can_visit_top_node():
                self.visit_top_node()

    def clear_path(self) -> None:
        for row in self.nodes:
            for node in row:
                node.previous_node = None
                if node.node_type not in {
                    NodeType.START,
                    NodeType.TARGET,
                    NodeType.WALL,
                }:
                    node.node_type = NodeType.FREE
        self.search_for_path = True
        self.current_node_coordinates = None
        self.coordinates_to_visit = []

    def get_path(self) -> None:
        current_node = self.nodes[self.current_node_coordinates.y][
            self.current_node_coordinates.x
        ].previous_node
        while current_node and current_node.previous_node:
            current_node.node_type = NodeType.PATH
            current_node = current_node.previous_node

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        for row in self.nodes:
            nodes = arcade.get_sprites_at_point((x, y), row)
            if nodes:
                self.engaged_node = nodes[0]

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        for row in self.nodes:
            nodes = arcade.get_sprites_at_point((x, y), row)
            if nodes:
                if self.node_placement_type == NodeType.WALL:
                    if nodes[0].node_type not in {NodeType.START, NodeType.TARGET}:
                        if nodes[0].node_type == NodeType.WALL:
                            nodes[0].node_type = NodeType.FREE
                        else:
                            nodes[0].node_type = NodeType.WALL
                        self.clear_path()
                elif self.node_placement_type == NodeType.START:
                    if nodes[0].node_type not in {NodeType.START, NodeType.TARGET}:
                        self.nodes[self.start_node_coordinates.y][
                            self.start_node_coordinates.x
                        ].node_type = NodeType.FREE
                        nodes[0].node_type = NodeType.START
                        self.start_node_coordinates = Coordinate(
                            int(nodes[0].left / GRID_SIZE),
                            int(nodes[0].bottom / GRID_SIZE),
                        )
                        self.clear_path()
                elif self.node_placement_type == NodeType.TARGET:
                    if nodes[0].node_type not in {NodeType.START, NodeType.TARGET}:
                        self.nodes[self.target_node_coordinates.y][
                            self.target_node_coordinates.x
                        ].node_type = NodeType.FREE
                        nodes[0].node_type = NodeType.TARGET
                        self.target_node_coordinates = Coordinate(
                            int(nodes[0].left / GRID_SIZE),
                            int(nodes[0].bottom / GRID_SIZE),
                        )
                        self.clear_path()

    def add_node_to_grid(self) -> None:
        pass

    def can_visit_left_node(self) -> bool:
        return self.current_node_coordinates.x != 0 and self.nodes[
            self.current_node_coordinates.y
        ][self.current_node_coordinates.x - 1].node_type not in {
            NodeType.EXPLORED,
            NodeType.START,
            NodeType.WALL,
        }

    def visit_left_node(self) -> None:
        self.coordinates_to_visit.append(
            Coordinate(
                self.current_node_coordinates.x - 1, self.current_node_coordinates.y
            )
        )
        self.nodes[self.current_node_coordinates.y][
            self.current_node_coordinates.x - 1
        ].node_type = NodeType.EXPLORED
        self.nodes[self.current_node_coordinates.y][
            self.current_node_coordinates.x - 1
        ].previous_node = self.nodes[self.current_node_coordinates.y][
            self.current_node_coordinates.x
        ]

    def can_visit_right_node(self) -> bool:
        return self.current_node_coordinates.x != len(
            self.nodes[self.current_node_coordinates.y]
        ) - 1 and self.nodes[self.current_node_coordinates.y][
            self.current_node_coordinates.x + 1
        ].node_type not in {
            NodeType.EXPLORED,
            NodeType.START,
            NodeType.WALL,
        }

    def visit_right_node(self) -> None:
        self.coordinates_to_visit.append(
            Coordinate(
                self.current_node_coordinates.x + 1, self.current_node_coordinates.y
            )
        )
        self.nodes[self.current_node_coordinates.y][
            self.current_node_coordinates.x + 1
        ].node_type = NodeType.EXPLORED
        self.nodes[self.current_node_coordinates.y][
            self.current_node_coordinates.x + 1
        ].previous_node = self.nodes[self.current_node_coordinates.y][
            self.current_node_coordinates.x
        ]

    def can_visit_bottom_node(self) -> bool:
        return self.current_node_coordinates.y != 0 and self.nodes[
            self.current_node_coordinates.y - 1
        ][self.current_node_coordinates.x].node_type not in {
            NodeType.EXPLORED,
            NodeType.START,
            NodeType.WALL,
        }

    def visit_bottom_node(self) -> None:
        self.coordinates_to_visit.append(
            Coordinate(
                self.current_node_coordinates.x, self.current_node_coordinates.y - 1
            )
        )
        self.nodes[self.current_node_coordinates.y - 1][
            self.current_node_coordinates.x
        ].node_type = NodeType.EXPLORED
        self.nodes[self.current_node_coordinates.y - 1][
            self.current_node_coordinates.x
        ].previous_node = self.nodes[self.current_node_coordinates.y][
            self.current_node_coordinates.x
        ]

    def can_visit_top_node(self) -> bool:
        return self.current_node_coordinates.y != len(self.nodes) - 1 and self.nodes[
            self.current_node_coordinates.y + 1
        ][self.current_node_coordinates.x].node_type not in {
            NodeType.EXPLORED,
            NodeType.START,
            NodeType.WALL,
        }

    def visit_top_node(self) -> None:
        self.coordinates_to_visit.append(
            Coordinate(
                self.current_node_coordinates.x, self.current_node_coordinates.y + 1
            )
        )
        self.nodes[self.current_node_coordinates.y + 1][
            self.current_node_coordinates.x
        ].node_type = NodeType.EXPLORED
        self.nodes[self.current_node_coordinates.y + 1][
            self.current_node_coordinates.x
        ].previous_node = self.nodes[self.current_node_coordinates.y][
            self.current_node_coordinates.x
        ]

    def on_draw(self) -> None:
        self.clear()
        self.draw_nodes()
        self.draw_grid()
        self.highlight_node()

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
                    case NodeType.PATH:
                        arcade.draw_rectangle_filled(
                            node.center_x,
                            node.center_y,
                            GRID_SIZE,
                            GRID_SIZE,
                            arcade.color.PINK,
                        )
                    case NodeType.WALL:
                        arcade.draw_rectangle_filled(
                            node.center_x,
                            node.center_y,
                            GRID_SIZE,
                            GRID_SIZE,
                            arcade.color.RED,
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

    def highlight_node(self) -> None:
        if self.engaged_node:
            match self.node_placement_type:
                case NodeType.WALL:
                    arcade.draw_rectangle_filled(
                        self.engaged_node.center_x,
                        self.engaged_node.center_y,
                        self.engaged_node.width,
                        self.engaged_node.height,
                        (255, 0, 0, 255 / 2),
                    )
                case NodeType.START:
                    arcade.draw_rectangle_filled(
                        self.engaged_node.center_x,
                        self.engaged_node.center_y,
                        self.engaged_node.width,
                        self.engaged_node.height,
                        (0, 255, 0, 255 / 2),
                    )
                case NodeType.TARGET:
                    arcade.draw_rectangle_filled(
                        self.engaged_node.center_x,
                        self.engaged_node.center_y,
                        self.engaged_node.width,
                        self.engaged_node.height,
                        (255, 255, 0, 255 / 2),
                    )


def main() -> None:
    PathFinding(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
