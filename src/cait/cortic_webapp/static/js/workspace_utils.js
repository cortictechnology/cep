/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021
  
 */

var current_workspace = "";

var start_new_workspace = false;

function replaceAll(str, find, replace) {
  return str.replace(new RegExp(find, 'g'), replace);
}

function stopVideoFeed() {
  topicMessage = new Paho.Message("VisionDown");
  topicMessage.topic = "cait/vision_control";
  client.publish(topicMessage)
}

function emptyVisionMode() {
  topicMessage = new Paho.Message("ResetMode");
  topicMessage.topic = "cait/vision_control";
  client.publish(topicMessage)
}

function stopVoice() {
  topicMessage = new Paho.Message("VoiceDown");
  topicMessage.topic = "cait/voice_control";
  client.publish(topicMessage)
}

function resetModules() {
  topicMessage = new Paho.Message("Reset");
  topicMessage.topic = "cait/module_states";
  client.publish(topicMessage)
}

var test;

function enableChildBlock(block) {
  var childBlks = block.childBlocks_;
  console.log(childBlks);
  if (childBlks.length > 0) {
    for (i in childBlks) {
      childBlks[i].setEnabled(true);
      if (childBlks[i].type == "add_control_hub") {
        if (childBlks[i].inputList[0].fieldRow[1].value_ != 'none') {
          var index = added_hubs.indexOf(childBlks[i].inputList[0].fieldRow[1].value_);
          if (index == -1) {
            added_hubs.push(childBlks[i].inputList[0].fieldRow[1].value_);
          }
        }
        if (childBlks[i].getSurroundParent().type != "init_control") {
          childBlks[i].setEnabled(false);
        }
        else {
          childBlks[i].setEnabled(true);
        }
      }
      if (childBlks[i].type == "init_vision" ||
        childBlks[i].type == "init_voice" ||
        childBlks[i].type == "init_nlp" ||
        childBlks[i].type == "init_control" ||
        childBlks[i].type == "init_smarthome") {
        if (childBlks[i].getSurroundParent().type != "setup_block") {
          childBlks[i].setEnabled(false);
        }
      }
      else {
        if (childBlks[i].getSurroundParent().type == "setup_block") {
          childBlks[i].setEnabled(false);
        }
      }
      enableChildBlock(childBlks[i]);
    }
  }
  else {
    return;
  }
}

function disableChildBlock(block) {
  var childBlks = block.childBlocks_;
  if (childBlks.length > 0) {
    for (i in childBlks) {
      childBlks[i].setEnabled(false);
      if (childBlks[i].type == "add_control_hub") {
        var allBlocks = workspace.getAllBlocks();
        var index = added_hubs.indexOf(childBlks[i].inputList[0].fieldRow[1].value_);
        if (index != -1) {
          var hub_still_exists = false;
          for (blk in allBlocks) {
            if (allBlocks[blk].type == "add_control_hub" && allBlocks[blk].isEnabled()) {
              if (allBlocks[blk].inputList[0].fieldRow[1].value_ == childBlks[i].inputList[0].fieldRow[1].value_) {
                hub_still_exists = true;
              }
            }
          }
          if (!hub_still_exists) {
            added_hubs.splice(index, 1);
          }
        }
      }
      if (childBlks[i].type == "init_vision" ||
        childBlks[i].type == "init_voice" ||
        childBlks[i].type == "init_nlp" ||
        childBlks[i].type == "init_control" ||
        childBlks[i].type == "add_control_hub" ||
        childBlks[i].type == "init_smarthome") {
        if (childBlks[i].getSurroundParent() != null) {
          if (childBlks[i].getSurroundParent().type == "setup_block") {
            childBlks[i].setEnabled(true);
          }
        }
      }
      else {
        if (childBlks[i].getSurroundParent() != null) {
          if (childBlks[i].getSurroundParent().type == "main_block") {
            childBlks[i].setEnabled(true);
          }
        }
      }
      disableChildBlock(childBlks[i]);
    }
  }
  else {
    return;
  }
}

function updateFunction(event) {
  var block = workspace.getBlockById(event.blockId);
  var allBlocks = workspace.getAllBlocks();
  if (event.type == Blockly.Events.BLOCK_CREATE) {
    block.contextMenu = false;
  }
  if (event.type == Blockly.Events.UI) {
    if (event.newValue != null) {
      if (event.newValue.indexOf("Robot Inventor") != -1) {
        topicMessage = new Paho.Message('Control Up,["' + event.newValue + '"]');
        topicMessage.topic = "cait/motor_control";
        client.publish(topicMessage)
      }
    }
  }
  if (event.type == Blockly.Events.BLOCK_CHANGE) {
    if (event.element == "field") {
      if (block.type == "add_control_hub") {
        if (event.oldValue == "none") {
          var index = added_hubs.indexOf(event.newValue);
          if (index == -1) {
            added_hubs.push(event.newValue);
          }
        }
        if (event.newValue == "none") {
          var index = added_hubs.indexOf(event.oldValue);
          if (index != -1) {
            added_hubs.splice(index, 1);
          }
        }
        else {
          var index = added_hubs.indexOf(event.newValue);
          if (index == -1) {
            added_hubs.push(event.newValue);
          }
          index = added_hubs.indexOf(event.oldValue);
          if (index != -1) {
            var hub_still_exists = false;
            for (blk in allBlocks) {
              if (allBlocks[blk].type == "add_control_hub" && allBlocks[blk].isEnabled()) {
                if (allBlocks[blk].inputList[0].fieldRow[1].value_ == event.oldValue) {
                  hub_still_exists = true;
                }
              }
            }
            if (!hub_still_exists) {
              added_hubs.splice(index, 1);
            }
          }
        }
        if (event.newValue.indexOf("Robot Inventor") != -1) {
          topicMessage = new Paho.Message('Control Up,["' + event.newValue + '"]');
          topicMessage.topic = "cait/motor_control";
          client.publish(topicMessage)
        }
      }
      if (event.oldValue == "color_name" || event.oldValue == "brightness_pct") {
        block.getInput("param_input").removeField('parameter');
      }
      if (event.newValue == "color_name" || event.newValue == "brightness_pct") {
        block.getInput("param_input").appendField(
          new Blockly.FieldTextInput(), "parameter"
        )
      }

      if (event.oldValue == "on device") {
        block.getInput("cloud_accounts").setVisible(true);
        block.getInput("ending").setVisible(true);
        block.getField("language").setVisible(true);
        block.render();
      }
      if (event.newValue == "on device") {
        block.getInput("cloud_accounts").setVisible(false);
        block.getInput("ending").setVisible(false);
        block.getField("language").setVisible(false);
        block.render();
      }
      if (event.oldValue == "virtual") {
        block.getInput("proc_param").removeField("on");
        block.getInput("proc_param").removeField("vision_proc");
      }

      if (event.newValue == "virtual") {
        block.getInput("proc_param").appendField(
          new Blockly.FieldLabel("on"), "on");
        block.getInput("proc_param").appendField(new Blockly.FieldDropdown(function () {
          var options = [];
          var vision_processors = virtual_processors['Vision'];
          if (vision_processors.length > 0) {
            for (i in vision_processors) {
              options.push([vision_processors[i], vision_processors[i]])
            }
          }
          else {
            options.push(['none', 'none']);
          }
          return options;
        }), 'vision_proc');
      }
    }
  }

  if (event.type == Blockly.Events.BLOCK_CREATE) {
    if (block.type == "setup_block") {
      for (blk in allBlocks) {
        if (allBlocks[blk].type == "setup_block" && allBlocks[blk] != block) {
          block.setEnabled(false);
          break;
        }
        else {
          block.setEnabled(true);
        }
      }
    }
    else if (block.type == "main_block") {
      var setuBlockExist = false;
      for (blk in allBlocks) {
        if (allBlocks[blk].type == "main_block" && allBlocks[blk] != block) {
          block.setEnabled(false);
          break;
        }
        else {
          block.setEnabled(true);
        }
        if (allBlocks[blk].type == "setup_block") {
          setuBlockExist = true;
        }
      }
      if (!setuBlockExist) {
        block.setEnabled(false);
      }
    }
  }

  if (event.type == Blockly.Events.BLOCK_MOVE) {
    var parentBlock = workspace.getBlockById(event.newParentId);
    if (block != null) {
      if (block.type == "init_vision" ||
        block.type == "init_vision_pi" ||
        block.type == "init_voice" ||
        block.type == "init_nlp" ||
        block.type == "init_control" ||
        block.type == "add_control_hub" ||
        block.type == "init_pid" ||
        block.type == "init_smarthome") {
        if (block.getSurroundParent() != null) {
          if (block.getSurroundParent().type == "setup_block") {
            block.setEnabled(true);
            if (block.type == "add_control_hub") {
              if (block.inputList[0].fieldRow[1].value_ != 'none') {
                var index = added_hubs.indexOf(block.inputList[0].fieldRow[1].value_);
                if (index == -1) {
                  added_hubs.push(block.inputList[0].fieldRow[1].value_);
                }
              }
            }
            enableChildBlock(block);
          }
          else {
            block.setEnabled(false);
            allBlocks = workspace.getAllBlocks();
            if (block.type == "add_control_hub") {
              var index = added_hubs.indexOf(block.inputList[0].fieldRow[1].value_);
              if (index != -1) {
                var hub_still_exists = false;
                for (blk in allBlocks) {
                  if (allBlocks[blk].type == "add_control_hub" && allBlocks[blk].isEnabled()) {
                    if (allBlocks[blk].inputList[0].fieldRow[1].value_ == block.inputList[0].fieldRow[1].value_) {
                      hub_still_exists = true;
                    }
                  }
                }
                if (!hub_still_exists) {
                  added_hubs.splice(index, 1);
                }
              }
            }
            disableChildBlock(block);
          }
        }
        else {
          block.setEnabled(false);
          allBlocks = workspace.getAllBlocks();
          if (block.type == "add_control_hub") {
            var index = added_hubs.indexOf(block.inputList[0].fieldRow[1].value_);
            if (index != -1) {
              var hub_still_exists = false;
              for (blk in allBlocks) {
                if (allBlocks[blk].type == "add_control_hub" && allBlocks[blk].isEnabled()) {
                  if (allBlocks[blk].inputList[0].fieldRow[1].value_ == block.inputList[0].fieldRow[1].value_) {
                    hub_still_exists = true;
                  }
                }
              }
              if (!hub_still_exists) {
                added_hubs.splice(index, 1);
              }
            }
          }
          disableChildBlock(block);
        }
      }

      else if (block.type == "setup_block") {
        var needsDisable = false;
        for (blk in allBlocks) {
          if (allBlocks[blk].type == "setup_block" && allBlocks[blk] != block) {
            if (allBlocks[blk].isEnabled()) {
              needsDisable = true;
            }
          }
        }
        if (needsDisable) {
          block.setEnabled(false);
        }
        for (blk in allBlocks) {
          if (allBlocks[blk].type == "main_block") {
            allBlocks[blk].setEnabled(true);
            break;
          }
        }
      }
      else if (block.type == "main_block") {
        var setuBlockExist = false;
        var needsDisable = false;
        for (blk in allBlocks) {
          if (allBlocks[blk].type == "main_block" && allBlocks[blk] != block) {
            if (allBlocks[blk].isEnabled()) {
              needsDisable = true;
            }
          }
        }
        if (needsDisable) {
          block.setEnabled(false);
        }
        for (blk in allBlocks) {
          if (allBlocks[blk].type == "setup_block") {
            setuBlockExist = true;
          }
        }
        if (!setuBlockExist) {
          block.setEnabled(false);
        }
      }
      else {
        var within_main_block = false;
        while (parentBlock != null) {
          if (parentBlock.type == "main_block" || parentBlock.type.indexOf('procedures_') != -1) {
            within_main_block = true;
            block.setEnabled(true);
            enableChildBlock(block);
            break;
          }
          else {
            parentBlock = parentBlock.parentBlock_;
          }
        }
        if (!within_main_block) {
          block.setEnabled(false);
          disableChildBlock(block);
          if (block.type.indexOf("vision_") != -1) {
            emptyVisionMode();
          }
        }
      }

      if (block.type == "add_control_hub") {
        if (block.getSurroundParent() != null) {
          if (block.getSurroundParent().type == "init_control") {
            block.setEnabled(true);
            enableChildBlock(block);
          }
          else {
            block.setEnabled(false);
            disableChildBlock(block);
          }
        }
      }

      if (block.type == "add_pipeline_node") {
        if (block.getSurroundParent() != null) {
          if (block.getSurroundParent().type == "init_vision") {
            block.setEnabled(true);
            enableChildBlock(block);
          }
          else {
            block.setEnabled(false);
            disableChildBlock(block);
          }
        }
      }

      if (block.getSurroundParent() != null) {
        if (block.getSurroundParent().type == "init_pid") {
          block.setEnabled(true);
        }
      }

      if (block.type == "set_parameter" && block.parentBlock_ != null) {
        block.setEnabled(true);
      }
      if (block.parentBlock_ != null) {
        if (block.parentBlock_.type == "set_parameter" && !block.parentBlock_.isDisabled) {
          block.setEnabled(true);
        }
      }
      if (block.type == "sleep" && block.parentBlock_ != null) {
        block.setEnabled(true);
      }
      if (block.parentBlock_ != null) {
        if (block.parentBlock_.type == "sleep" && !block.parentBlock_.isDisabled) {
          block.setEnabled(true);
        }
      }
      if (block.type.indexOf('procedures_') != -1) {
        if (block.tooltip.indexOf("Creates a function") == 0) {
          block.setEnabled(true);
          enableChildBlock(block);
        }
      }
    }
  }

  if (event.type == Blockly.Events.BLOCK_DELETE) {
    if (event.oldXml.getAttribute("type") == "add_control_hub") {
      var index = added_hubs.indexOf(event.oldXml.getRootNode().firstElementChild.textContent);
      allBlocks = workspace.getAllBlocks();
      if (index != -1) {
        var hub_still_exists = false;
        for (blk in allBlocks) {
          if (allBlocks[blk].type == "add_control_hub" && allBlocks[blk].isEnabled()) {
            if (allBlocks[blk].inputList[0].fieldRow[1].value_ == event.oldXml.getRootNode().firstElementChild.textContent) {
              hub_still_exists = true;
            }
          }
        }
        if (!hub_still_exists) {
          added_hubs.splice(index, 1);
        }
      }
    }

    var setupBlockRemains = false;
    for (blk in allBlocks) {
      if (allBlocks[blk].type == "setup_block") {
        setupBlockRemains = true;
      }
    }
    if (event.oldXml.getAttribute("type") == "setup_block") {
      for (blk in allBlocks) {
        if (allBlocks[blk].type == "setup_block") {
          allBlocks[blk].setEnabled(true);
          break;
        }
      }
      for (blk in allBlocks) {
        if (allBlocks[blk].type == "main_block") {
          if (setupBlockRemains) {
            allBlocks[blk].setEnabled(true);
            break;
          }
          else {
            allBlocks[blk].setEnabled(false);
          }
        }
      }
    }
    else if (event.oldXml.getAttribute("type") == "main_block") {
      for (blk in allBlocks) {
        if (allBlocks[blk].type == "main_block") {
          if (setupBlockRemains) {
            allBlocks[blk].setEnabled(true);
            break;
          }
        }
      }
    }
  }
  current_workspace = workspace;
}

var stopCode = false;

function highlightBlock(id) {
  workspace.highlightBlock(id);
}

function resetStepUi(clearOutput) {
  workspace.highlightBlock(null);
}

function run_code() {
  //var xml = Blockly.Xml.workspaceToDom(workspace);
  //var xml_text = Blockly.Xml.domToText(xml);
  //console.log(xml_text);
  stopCode = false;
  Blockly.JavaScript.addReservedWords('code');
  Blockly.JavaScript.STATEMENT_PREFIX = 'highlightBlock(%1);\n';
  Blockly.JavaScript.addReservedWords('highlightBlock');
  resetStepUi(true);
  try {
    var code = Blockly.JavaScript.workspaceToCode(workspace);
    save_workspace(true);
    if (code.indexOf("await") != -1) {
      if (code.indexOf("function") != -1) {
        if (code[code.indexOf("function") - 1] != '_' || code[code.indexOf("function") + 8] != '_') {
          code = replaceAll(code, 'function', 'async function');
        }
      }
      async_function = [];
      index = 0;
      while (code.indexOf("async function", index) != -1) {
        begin_idx = code.indexOf("async function", index) + 15;
        end_idx = code.indexOf("(", begin_idx);
        func_name = code.substring(begin_idx, end_idx);
        if (func_name.indexOf("async function") != -1) {
          end_idx = begin_idx;
        }
        else {
          async_function.push(func_name);
        }
        index = end_idx;
      }
      //console.log("Async Functions: " + async_function);
      init_idx = code.indexOf("await cait_init_");
      runtime_code = code.substring(init_idx, code.length);
      for (f in async_function) {
        runtime_code = replaceAll(runtime_code, async_function[f], "await " + async_function[f]);
      }
      code = code.substring(0, init_idx) + runtime_code;
      code = code + "\n resetStepUi(true);\n"
      code = "(async () => {" + code + "})();";
    }
    var ready_to_execute_code = true;
    for (i in vision_func) {
      if (code.indexOf(vision_func[i]) != -1) {
        if (code.indexOf('init_vision') == -1) {
          alert(localizedStrings.visNotInit[locale]);
          ready_to_execute_code = false;
          break;
        }
      }
    }
    var missing_oakd_nodes = [];
    for (i in vision_func_dependent_blocks) {
      if (code.indexOf(i) != -1) {
        var dependent_blocks = vision_func_dependent_blocks[i];
        for (d in dependent_blocks) {
          var blk = dependent_blocks[d];
          if (typeof(blk) == "object" ){
            var node_present = false;
            var missing_node = "";
            for (j in blk) {
              if (code.indexOf(blk[j]) != -1) {
                node_present = true;
              }
              else {
                if (missing_node == "") {
                  missing_node = blk[j];
                }
                else {
                  missing_node = missing_node + " or " + blk[j];
                }
              }
            }
            if (!node_present) {
              missing_oakd_nodes.push(missing_node);
            }
          }
          else {
            console.log(blk);
            if (code.indexOf(blk) == -1) {
              missing_oakd_nodes.push(blk);
            }
          }
        }
      }
    }
    if (missing_oakd_nodes.length > 0) {
      alert("You need to add these nodes in the initialization block: " + String(missing_oakd_nodes));
      ready_to_execute_code = false;
    }
    for (i in speech_func) {
      if (code.indexOf(speech_func[i]) != -1) {
        if (code.indexOf('init_voice') == -1) {
          alert(localizedStrings.voiceNotInit[locale]);
          ready_to_execute_code = false;
          break;
        }
      }
    }
    for (i in nlp_func) {
      if (code.indexOf(nlp_func[i]) != -1) {
        if (code.indexOf('init_nlp') == -1) {
          alert(localizedStrings.nlpNotInit[locale]);
          ready_to_execute_code = false;
          break;
        }
      }
    }
    for (i in control_func) {
      if (code.indexOf(control_func[i]) != -1) {
        if (code.indexOf('init_control') == -1) {
          alert(localizedStrings.controlNotInit[locale]);
          ready_to_execute_code = false;
          break;
        }
      }
    }
    for (i in smart_home_func) {
      if (code.indexOf(smart_home_func[i]) != -1) {
        if (code.indexOf('init_smarthome') == -1) {
          alert(localizedStrings.sHomeNotInit[locale]);
          ready_to_execute_code = false;
          break;
        }
      }
    }
    console.log(code);
    if (ready_to_execute_code) {
      eval(code);
    }
  } catch (e) {
    alert(e.message);
  }
}

async function release_components() {
  const res = await $.ajax({
    url: "/release_components",
    type: 'POST',
    data: {}
  });
}

$(document).ready(function () {
  if (window.location.hash == '#reload') {
    onReload();
  }
});

function onReload() {
  window.location.hash = '';
  load_workspace(true);
}

async function stop_code() {
  //await save_workspace(true);
  //window.location.hash = '#reload';
  location.reload();
}

async function gen_py_code() {
  Blockly.Python.addReservedWords('code');
  var code = Blockly.Python.workspaceToCode(workspace);
  console.log(code);
  var filename;
  filename = prompt(localizedStrings.genPyName[locale]);
  if (filename != '') {
    const res = await $.ajax({
      url: "/savepythoncode",
      type: 'POST',
      data: {
        "filename": filename,
        "code": code
      }
    });
  }
}

async function gen_py_notebook() {
  Blockly.Python.addReservedWords('code');
  var code = Blockly.Python.workspaceToCode(workspace);
  var filename;
  filename = prompt(localizedStrings.genPyNBName[locale]);
  if (filename != '') {
    const res = await $.ajax({
      url: "/savenotebook",
      type: 'POST',
      data: {
        "filename": filename,
        "code": code
      }
    });
  }
}

async function save_workspace(autosave = false) {
  var xml = Blockly.Xml.workspaceToDom(workspace);
  var xml_text = Blockly.Xml.domToText(xml);
  var filename;
  var path;
  if (autosave) {
    save_type = "autosave";
    filename = "workspace_autosave.xml";
  }
  else {
    save_type = "save";
    filename = prompt(localizedStrings.saveName[locale]);
  }
  if (filename != '') {
    const res = await $.ajax({
      url: "/saveworkspace",
      type: 'POST',
      data: {
        "filename": filename,
        "xml_text": xml_text,
        "save_type": save_type
      }
    });
  }
}

async function new_workspace() {
  const res = await $.ajax({
    url: "/clearcache",
    type: 'POST',
    data: {}
  });
  start_new_workspace = true;
  location.reload();
}

async function new_workspace_save() {
  await save_workspace();
}

async function load_workspace(from_autosave = false) {
  var filename;
  var path;
  var autosave;
  if (from_autosave) {
    save_type = "autosave";
    filename = "workspace_autosave.xml";
  }
  else {
    save_type = "save";
    filename = prompt(localizedStrings.loadName[locale]);
  }
  const res = await $.ajax({
    url: "/loadworkspace",
    type: 'POST',
    data: { "filename": filename, "save_type": save_type }
  });
  // console.log(res);
  xml_text = res['xml_text'];
  if (xml_text != '') {
    var xml = Blockly.Xml.textToDom(xml_text);
    Blockly.Xml.domToWorkspace(xml, workspace);
  }
}