import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import Modal from 'react-modal';
import './NodeGraph.css';
import NYCTripModalContent from './NYCTripModalContent';

Modal.setAppElement('#root');

function NodeGraph({ nodesData }) {
    const svgRef = useRef();
    const [modalIsOpen, setModalIsOpen] = useState(false);
    const [selectedNode, setSelectedNode] = useState(null);

    useEffect(() => {
        const width = 1200;
        const height = 1200;

        const svg = d3.select(svgRef.current)
            .attr("width", width)
            .attr("height", height);

        // Clear the SVG before drawing
        svg.selectAll("*").remove();

        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {
                svg.attr("transform", event.transform);
            });

        svg.call(zoom);

        const container = svg.append("g");

        const simulation = d3.forceSimulation(nodesData.nodes)
            .force("link", d3.forceLink(nodesData.links).id(d => d.id).distance(200))
            .force("charge", d3.forceManyBody().strength(-1000))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide(70));

        const link = container.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(nodesData.links)
            .enter().append("line")
            .attr("class", "link");

        const node = container.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(nodesData.nodes)
            .enter().append("circle")
            .attr("class", d => d.id === 'Self' ? 'center-node' : 'node')
            .attr("r", d => d.id === 'Self' ? 30 : 20)
            .on("click", handleNodeClick)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        const label = container.append("g")
            .attr("class", "labels")
            .selectAll("text")
            .data(nodesData.nodes)
            .enter().append("text")
            .attr("class", d => d.id === 'Self' ? 'center-label label' : 'label')
            .text(d => d.id);

        const description = container.append("g")
            .attr("class", "descriptions")
            .selectAll("text")
            .data(nodesData.nodes.filter(d => d.description))
            .enter().append("text")
            .attr("class", "description")
            .text(d => d.description);

        simulation
            .nodes(nodesData.nodes)
            .on("tick", ticked);

        simulation.force("link")
            .links(nodesData.links);

        function ticked() {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            label
                .attr("x", d => d.x)
                .attr("y", d => d.y + 5); // Adjust this value to vertically center the text

            description
                .attr("x", d => d.x)
                .attr("y", d => d.y + 20); // Adjust this value for description placement
        }

        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        function handleNodeClick(event, d) {
            setSelectedNode(d);
            setModalIsOpen(true);
        }

    }, [nodesData]);

    const getModalContent = (node) => {
        if (node && node.modalContentComponent === 'NYCTripModalContent') {
            return <NYCTripModalContent node={node} />;
        }
        return (
            <div>
                <h2>{node.id}</h2>
                <p>{node.description}</p>
            </div>
        );
    };

    return (
        <div className="NodeGraph">
            <svg ref={svgRef}></svg>
            <Modal
                isOpen={modalIsOpen}
                onRequestClose={() => setModalIsOpen(false)}
                contentLabel="Node Details"
                className="Modal"
                overlayClassName="Overlay"
            >
                {selectedNode && getModalContent(selectedNode)}
                <button onClick={() => setModalIsOpen(false)}>Close</button>
            </Modal>
        </div>
    );
}

export default NodeGraph;
