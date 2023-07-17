from pyqtgraph.parametertree import Parameter,registerParameterType
from freemocap_utils.constants import(
    TASK_INTERPOLATION,
    TASK_FILTERING,
    TASK_FINDING_GOOD_FRAME,
    TASK_SKELETON_ROTATION,
    PARAM_METHOD,
    PARAM_ORDER,
    PARAM_CUTOFF_FREQUENCY,
    PARAM_SAMPLING_RATE,
    PARAM_ROTATE_DATA,
    PARAM_AUTO_FIND_GOOD_FRAME,
    PARAM_GOOD_FRAME
)


interpolation_settings = [
    {"name": TASK_INTERPOLATION.title(), "type": "group", "children": [
        {"name": PARAM_METHOD, "type": "list", "values": ["linear", "cubic", "spline"]},
        {"name": "Order (only used in spline interpolation)", "type": "int", "value":3, "step":1}
    ]}
]

filter_settings = [
        {"name": TASK_FILTERING.title(), "type": "group", "children": [
        {"name": "Filter Type", "type": "list", "values": ["Butterworth Low Pass"]},
        {"name": PARAM_ORDER, "type":"int","value":4, "step":.1},
        {"name": PARAM_CUTOFF_FREQUENCY, "type": "float", "value": 6.0, "step": 0.1},
        {"name": PARAM_SAMPLING_RATE, "type": "float", "value": 30.0, "step": 0.1},
    ]}
]

rotation_settings = [
    {"name": TASK_SKELETON_ROTATION.title(), "type": "group", "children": [
        {"name": PARAM_ROTATE_DATA, "type": "list", "values": ["None", "Rotate around x", "Foot/Spine Rotation"], "value": "None"},
        {"name": "Instructions", "type": "str", "value": "Uncheck 'Auto-find Good Frame' to type in the good frame manually.", "readonly": True},
        {"name": PARAM_AUTO_FIND_GOOD_FRAME, "type": "bool", "value": True},
        {"name": PARAM_GOOD_FRAME, "type": "str", "value": "", "step": 1},
    ]}
]

class FootSpineRotationParam:
    def __init__(self, auto_find_good_frame_param, good_frame_param):
        self.auto_find_good_frame_param = auto_find_good_frame_param
        self.good_frame_param = good_frame_param
        self.auto_find_good_frame_param.sigValueChanged.connect(self.auto_find_good_frame_changed)

    def enable(self):
        self.auto_find_good_frame_param.setOpts(enabled=True)
        # Make sure to disable the good_frame_param when enabling this group.
        self.good_frame_param.setOpts(enabled=False)
        # As per your description, auto_find_good_frame_param should be True by default.
        self.auto_find_good_frame_param.setValue(True)

    def disable(self):
        self.auto_find_good_frame_param.setOpts(enabled=False)
        self.good_frame_param.setOpts(enabled=False)

    def auto_find_good_frame_changed(self, value):
        if value.value():
            self.good_frame_param.setValue("")
            self.good_frame_param.setOpts(enabled=False, readonly=True)
        else:
            if not self.good_frame_param.value():
                self.good_frame_param.setValue("0")
            self.good_frame_param.setOpts(enabled=True, readonly=False)


class CustomRotationParam(Parameter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rotate_data_param = self.child(TASK_SKELETON_ROTATION.title()).child(PARAM_ROTATE_DATA)
        auto_find_good_frame_param = self.child(TASK_SKELETON_ROTATION.title()).child(PARAM_AUTO_FIND_GOOD_FRAME)
        good_frame_param = self.child(TASK_SKELETON_ROTATION.title()).child(PARAM_GOOD_FRAME)
        self.foot_spine_rotation = FootSpineRotationParam(auto_find_good_frame_param, good_frame_param)
        self.rotate_data_param.sigValueChanged.connect(self.rotate_data_changed)

    def rotate_data_changed(self, value):
        rotation_mode = value.value()
        if rotation_mode == "Foot/Spine Rotation":
            self.foot_spine_rotation.enable()
        else:
            self.foot_spine_rotation.disable()





interpolation_params = Parameter.create(name='interp_params', type='group', children=interpolation_settings)
filter_params = Parameter.create(name='filter_params',type='group', children=filter_settings )

registerParameterType('CustomRotationParam',CustomRotationParam)
rotation_params = Parameter.create(name='rotation_params', type='CustomRotationParam', children=rotation_settings) #the 'type' here refers to the parameter type we made the line above



if __name__ == "__main__":

    def get_all_parameter_values(parameter_object):
        values = {}
        for child in parameter_object.children(): #using this just to access the second level of the parameter tree
            if child.hasChildren():
                for grandchild in child.children():
                    values[grandchild.name()] = grandchild.value()
            else:
                values[child.name()] = child.value()
        return values

    values = get_all_parameter_values(filter_params)
    f =2 