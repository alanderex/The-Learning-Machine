let d8r = (function(d3){

  // Fixed node IDs
  const fixedNodeIDs = ["happy","sad","disgusted","fearful","angry","surprised"];

  // Six random numbers that add up to x
  function nodeLinks(x) {
    let rndNmbrs = [];
    for(let i = 0; i < 6; i++){
      rndNmbrs.push(Math.random());
    }
    let total = rndNmbrs.reduce(
      (accumulator, currentValue) => accumulator + currentValue,
      0
    );
    let multiplier = x/total;
    for(let i = 0; i < 6; i ++){
      rndNmbrs[i] = rndNmbrs[i] * multiplier;
    }
    return rndNmbrs;
  }

  // Get random int inclusive of min and max
  // from: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random
  function getRandomIntInclusive(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min; //The maximum is inclusive and the minimum is inclusive
  }

  function getRandomFace() {
    let index = getRandomIntInclusive(1, 20);
    let emotion = ["angry","disgust","fear","happy","neutral","sad","surprise"][getRandomIntInclusive(0,6)]
    return "./faces/" + emotion + "/" + emotion + "_" + index + ".png";
  }

  // UUID generator (https://stackoverflow.com/questions/105034/create-guid-uuid-in-javascript)
  function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
  }

  function makeFixedNodes(ids){
    let fxNodes = [];
    for(let i = 0; i < 6; i++){
      fxNodes.push({id: ids[i], group:"target", image:ids[i] + ".svg"});
    }
    return {nodes: fxNodes, links: []};
  }

  const fixedNodes = makeFixedNodes(fixedNodeIDs);

  function getNode(thisID, fixedNodeIDs, outwardLinks, image = getRandomFace()){
    let node = {
      id: thisID,
      group: "data",
      image: image
    };
    let links = [];
    for(let i = 0; i < 6; i++){
      let link = {
        //id: uuidv4(), // not needed if the id is made from the source and target nodes
        source: thisID,
        target: fixedNodeIDs[i],
        value: outwardLinks[i]
      };
      links.push(link);
    }
    return {nodes: [node], links: links};
  }

  // Convert server response node into node array node
  function toNodeArrayNode(serverResponseNode){
    let linksArray = [];
    for(let i = 0; i < 6; i++){
      let linkObject = {
        source: serverResponseNode.id,
        target: fixedNodeIDs[i],
        value: serverResponseNode.links[fixedNodeIDs[i]]
      };
      linksArray.push(linkObject);
    }

    let nodeArrayNode = {
      nodes:[
        {
          id: serverResponseNode.id,
          group: "data",
          image: serverResponseNode.image
        }
      ],
      links: linksArray
    };
    return nodeArrayNode;
  }

  function getNodeArray(lngth){
    let nodes = [];
    for(let i = 0; i < lngth; i++){
      nodes.push(getNode(uuidv4(),fixedNodeIDs,nodeLinks(1)));
    }
    return nodes;
  }

  function updateNode(thisNode, newLinks){
    for(let i = 0; i < 6; i++){
      thisNode.links[i].value = newLinks[i];
    }
    return thisNode;
  }

  function refreshNodeArray(nodeArray, serverResponse){
    let nodeArrayIds = nodeArray.map((x) => x.nodes[0].id);

    for(let i = 0; i < serverResponse.length; i++){
      if(nodeArrayIds.includes(serverResponse[i].id)){
        let uNode = nodeArray.find((x) => x.nodes[0].id === serverResponse[i].id);
        for(let j = 0; j < uNode.links.length; j++){
          uNode.links[j].value = serverResponse[i][uNode.links[j].target.id];
        }
      } else {
        let outwardLinks = [];
        fixedNodeIDs.forEach((x) => outwardLinks.push(serverResponse[i].links[x]));
        thisID, fixedNodeIDs, outwardLinks, image
        let nuNode = getNode(serverResponse[i].id, fixedNodeIDs, outwardLinks, serverResponse.image);
        nodeArray.push(nuNode);
      }
    }
    return nodeArray;
  }

  function simpleUpdateNodeArray(nodeArray){
    for(let i = 0; i < nodeArray.length; i++){
      nodeArray[i] = updateNode(nodeArray[i],nodeLinks(1));
    }
    //console.log(nodeArray);
    return nodeArray;
  }

  function updateNodeArray(nodeArray, add = 0, remove = 0){
    for(let i = 0; i < nodeArray.length; i++){
      nodeArray[i] = updateNode(nodeArray[i],nodeLinks(1));
    }
    if(remove > 0) {
      for(let i = 0; i < remove; i++){
        nodeArray.pop();
      }
    }
    if(add > 0) {
      for(let i = 0; i < add; i++){
        nodeArray.push(getNode(uuidv4(),fixedNodeIDs,nodeLinks(1)));
      }
    }
    return nodeArray;
  }

  function compileData(nodeArray){
    let dataC = nodeArray.reduce(joinNodesReducer);
    dataC = {nodes: fixedNodes.nodes.concat(dataC.nodes), links: dataC.links};
    return dataC;
  }

  const joinNodesReducer = (acc, cur) => {
    return {nodes: acc.nodes.concat(cur.nodes),links: acc.links.concat(cur.links)};
  }

  function hexagon(n, cx, cy, gs){
    switch(n){
      case 0:
        return [cx - gs, cy - (Math.sqrt(3)*gs)];
        break;
      case 1:
        return [cx + gs, cy - (Math.sqrt(3)*gs)];
        break;
      case 2:
        return [cx + 2 * gs, cy];
        break;
      case 3:
        return [cx + gs, cy + (Math.sqrt(3)*gs)];
        break;
      case 4:
        return [cx - gs, cy + (Math.sqrt(3)*gs)];
        break;
      case 5:
        return [cx - 2 * gs, cy];
        break;
    }
  }

  function hexagonArray(cx, cy, gs){
    return [
      {x: cx - gs, y: cy - (Math.sqrt(3)*gs)},
      {x: cx + gs, y: cy - (Math.sqrt(3)*gs)},
      {x: cx + 2 * gs, y: cy},
      {x: cx + gs, y: cy + (Math.sqrt(3)*gs)},
      {x: cx - gs, y: cy + (Math.sqrt(3)*gs)},
      {x: cx - 2 * gs, y: cy}
    ]
  }

  function dist(x1, y1, x2, y2) {
    let xs = x2 - x1;
    let ys = y2 - y1;
    xs *= xs;
    ys *= ys;
    return(Math.sqrt(xs + ys));
  }

  return {
    fixedNodeIDs: fixedNodeIDs,
    nodeLinks: nodeLinks,
    uuidv4: uuidv4,
    makeFixedNodes: makeFixedNodes,
    fixedNodes: fixedNodes,
    getNode: getNode,
    getNodeArray: getNodeArray,
    toNodeArrayNode: toNodeArrayNode,
    updateNode: updateNode,
    updateNodeArray: updateNodeArray,
    refreshNodeArray: refreshNodeArray,
    simpleUpdateNodeArray: simpleUpdateNodeArray,
    compileData: compileData,
    joinNodesReducer: joinNodesReducer,
    hexagon: hexagon,
    hexagonArray: hexagonArray,
    dist: dist
  };
})(d3);
