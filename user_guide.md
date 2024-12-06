

## Run Configuration

While instantiated statistics and summarisers can be passed to the `Calculator` class and utilised as is (with pre-defined parameters), when the parameterisation scheme becomes large it is more convenient to provide a configuration. This method is also required when utilising the distributed computing component.

### General Structure

Configuration can be provided in code or via a file. The format required will be similarly split into two sections: `Statistics` and `Summarisers`. Each statistic defined under the `Statistics` section must be unique, but summarisers defined under the `Summariser` section can appear multiple times. The hierarchy for defining the scheme is as follows:

    Statistics
	    1stStatisticName
		   parameters
	    2ndStatisticName
		   parameters
	    .
	    .
	    .
	    nthStatisticName
		   parameters
	
	Summarisers
		1stSummariserName:
			Parameters:
				parameters
			Constraints:
				Statistics
		.
		.
		.
		mthSummariserName:
			.
			.
			.

Note: sectioned under `Constraints` you can find a reference to `Statistics`, which indicates that the structure within this section mirrors that of the `Statistics` section.

We now provide specifications for each supported format. Later, we will provide a motivating example to illustrate the structure further.

### YAML

The *pyspi* package upon which this library is based utilised YAML files to specify various configuration parameters. We have retained this use but simplified the required format. Run configuration now only requires information relevant to statistic selection and computation. Several pre-defined YAML configuration files will be available as part of the release that can be used directly or as a baseline for tailoring your own configuration. YAML provides arguably the cleaning depiction of the required hierarchy.

#### Statistics

Each statistic specified must have a unique name. Variations of the same statistic are specified by different parameterisation schemes. Under the statistic name, a `-` symbol declares the beginning of a new parameterisation, with each subsequent line defining a configured parameter and value.

    Statistics:
	    1stStatisticName:
		    - parameter: value
		2ndStatisticName:
			- parameter_1: first_parameter_1_value
			  parameter_2: first_parameter_2_value
			- parameter_1 : second_parameter_1_value
			  parameter_2 : second_parameter_2_value
			...
			- parameter_1: mth_parameter_1_value
			- parameter_2: mth_parameter_2_value
		...
		ithStatisticName:
			- parameter_1 : value
			  parameter_2 : value
	
#### Summarisers

Summarisers are defined in a similar way, however there are some key differences as mentioned previously. Firstly, they provide an extra layer of configuration to support constraints on the statistics they're applied to in the run. Secondly, a single summariser can appear more than once unlike with statistics. This is to facilitate the possibility of constraining a certain variant of summariser to a certain variants of statistics:

	Summarisers:
		- 1stSummariserName:
			Parameters:
				- parameter_1 : value
			Constraints:
				1stStatisticName:
				2ndStatisticName:
					- parameter_1 : value
		- 1stSummariserName:
			Parameters:
				- parameter_1 : different_value
			Constraints:
				3rdStatisticName:
					- parameter_1 : value
				4thStatisticName:
					- parameter_1 : value
					- parameter_2 : value
		- 2ndSummariserName:
			- Parameters:
				- parameter_1 : value
		...
		- jthSummariserName:
			...

As indicated in the **General Structure** section, the `Constraints` section of the `Summariser` configuration follows the same structure as in `Statistics`.

#### Summary Statistics

Finally, the all-in-one summary statistics are configured under the `SummaryStatistic` section:

    SummaryStatistics:
		1stSummaryStatisticName:
			- parameter_1 : value
				  
		2ndSummaryStatisticName
			- parameter_1 : value
			- parameter_2 : value
			  ...
			- parameter_p : value
		...
		kthSummaryStatisticName:
			...

### JSON File

JSON files specify the configuration in a very similar fashion, albeit with the popular JSON format. While slightly longer than the YAML configuration, JSON has the advantage of being naturally comparable to the Python dictionary object

#### Statistics

The general format for the `Statistics` object is as below

    {
	    "Statistics" : {
		    "1stStatisticName" : {
		    }
	    }
	}



#### Summarisers
#### SummaryStatistics

### Dictionary Object

An in-memory dictionary object can be provided instead. The required structure is identical to the **JSON** provided in the above section.

### Motivating Example

To better describe the requirements for the run configuration, we'll provide an example applied to an $n \times p$ dataset:

#### Run Configuration

We'll derive the following general statistics:

- Statistic 1: EmpiricalCovariance [Output: $p \times p$ matrix]
- Statistic 2: EllipticEnvelope [Output: $p \times p$ matrix]
	- Variant: Squared
- Statistic 3: PairwiseDistance [Output: $n \times n$ matrix]
	- Variant: Euclidean
- Statistic 4: InformationGeometricConditionalIndependence (ICGI) - [Output: $p \times p$ matrix]
	- Variant: Variables
- Statistic 5: InformationGeometricConditionalIndependence (ICGI) - [Output: $n \times n$ matrix]
	- Variant: Observations

Apply the following summaries to these statistics:

- Summariser 3: MatrixDeterminant [Output: $5$-vector]
	- Variants: Scaled
	- Statistics: All Except 5
- Summariser 4: Moments [Output: $6$-vector ($3$ moments for $2$ statistics)]
	- Selection: First 3
	- Statistics: 3, 5

And finally include the following fully defined summary statistics:
- SummaryStatistic 1: PCAVarianceExplained [Output: $2$-vector]
	- Selection: First 2
- SummaryStatistic 2: PCALoadings; [Output: $2p$-vector ($2$ loadings for $p$ variables)]
	- Selection: First 2

Total number of summary scalars: $13 + 2p$. Thus the output from this scheme will be a single row-wise $(13 + 2p)$-vector as a numpy array. 

#### YAML File

	Statistics:
	    EmpiricalCovariance:
	    EllipticEnvelope:
		    - squared: True
	    PairwiseDistance:
		    - metric: "euclidean"
	    IGCI:
		    - transpose: False
		    - transpose: True
	    
    Summaries:
	    PCAVarianceExplained:
		    Parameters:
			    - first: 2
	    PCALoadings:
		    Parameters:
			    - first: 2
			Constraints:
				EllipticEnvelope
				PairwiseDistance
				IGCI:
					- transpose : False				
		MatrixDeterminant:
			Parameters:
				- scaled: True
			Constraints:
				¬IGCI
					-transpose: False
		Moments:
			Parameters:
				- first: 3
			Constraints:
				PairwiseDistance
				IGCI:
					- transpose: True

**Important notes:**
- The `Constraints` subsection under each summary, which limits the application of the summary to specific statistics. 
- Specific parameterised statistic variants are referenced through the same structure present in the `Statistics` section.
- The not sign `¬` is used in the `Constrants` section to indicate all except a particular statistic. This can be seen under the `MatrixDeterminant` summary constraints for `ICGI`.

#### JSON File

    {
	    "Statistics" : {
		    "EmpiricalCovariance" : [],
		    "EllipticEnvelope" : [
			    {"squared" : true}
			],
		    "PairwiseDistance": [
			    {"metric" : "euclidean"}
			],
		    "IGCI": [
			    {"tranpose" : false}, 
			    {"transpose" : true}
			]
		},
	    
	    "Summaries": {
		    "PCAVarianceExplained": {
			    "Parameters": [
					{"first": 2}
				]
			},
		    "PCALoadings": {
			    "Parameters" : [
					{"first": 2}
				],
				"Constraints" : {
					"EllipticEnvelope" : [],
					"PairwiseDistance" : [],
					"IGCI" : [{"transpose" : false}]
				}
			},
			"MatrixDeterminant": {
				"Parameters" : [
					{"scaled": true}
				],
				"Constraints" : {
					"¬ICGI" : [
						{"transpose" : false}
					]
				}
			},
			"Moments": {
				"Parameters" : [
					{"first": 3}
				],
				"Constraints" : {
					"PairwiseDistance" : []
					"IGCI" : [
						{"transpose" : true}
					]					
				}
			}
		}
	}

**Important notes:**
- The `Constraints` subsection under each summary, which limits the application of the summary to specific statistics. 
- Specific parameterised statistic variants are referenced through the same structure present in the `Statistics` section.
- The not sign `¬` is used in the `Constrants` section to indicate all except a particular statistic. This can be seen under the `MatrixDeterminant` summary constraints for `ICGI`.



## Defining Custom Statistics and Summarizers

Two ways of defining a defining statistic can be supported. Some summaries are general and can be applied to any statistic, for example the first $n$ eigenvalues of highest modulus can be taken from any statistic with sufficient dimensionality. In other cases, a summary will be very specifically tied to the statistic.

### Generalised Flow:

In this case, either a custom statistic is defined or a summary (or both!), there need not be any link between them. In either case, the defined object must inherit from the applicable *pyspc* base object.

#### Statistic

The custom statistic inherits from the base `Statistic` class and **must** implement the `compute()` method, returning a numpy array (type `np.ndarray`):

    from pyspc import Statistic
    
    class MyStatistic(Statistic):
    
	    def __init__(self, stat_param_1, stat_param_2, ..., stat_param_n):
		    ... implemented code ...
		    
		def compute() -> np.ndarray:
			... implemented code ...
			return np.ndarray

#### Summarizer

Similarly, the custom statistic class, the custom summarizer inherits from the base `Summariser` class and **must** implement the `summarise()` method, returning a numpy array (type `np.ndarray`):

    from pyspc import Summariser
    
    class MySummariser(Summariser):
    
	    def __init__(self, summary_param_1, summary_param_2, ..., summary_param_m):
		    ... implemented code ...
		    
		def summarise() -> np.ndarray:
			... implemented code ...
			return np.ndarray

### All in One:

For statistics and summaries that need to be paired together specifically, an all in one class can be used instead which performs both the statistic computation and summary in one shot. The custom object inherits from the base `SummaryStatistic` class and **must* implement the `summarise()` method, returning a numpy array (type `np.ndarray`):

    from pyspc import SummaryStatistic
    
    class MySummaryStatistic(SummaryStatistic):
    
	    def __init__(self, 
		    stat_param_1, 
		    stat_param_2, 
		    ..., 
		    stat_param_n,
		    summary_param_1,
		    summary_param_2,
		    ...,
		    summary_param_m):
		    
		    ... implemented code ...
		    
		def summarise() -> np.ndarray:
			... implemented code ...
			return np.ndarray
			
The main distinction from the **Generalised Flow** is that a `SummaryStatistic` is self contained and will not be subjected to summarisation from other registered `Summariser` objects by the `Calculator` class.

### Registering Custom Objects

Once custom objects are defined, they need to be registered for use with the applicable `Calculator` object. Registry can be performed in a variety of ways depending on the use case:

#### Specific Instances

A specific instance of the object with parameters pre-defined can be registered:

    calc = Calculator(**calc_params)
    my_stat = MyStatistic(**statistic_params)
    my_summarizer = MySummariser(**summary_params)
    my_summary_stat = MySummaryStatistic(**statistic_params, **summary_params)
    calc.register_custom_object(my_stat)
    calc.register_custom_object(my_summarizer)
    calc.register_custom_object(my_summary_stat)

As these are instances of the custom object, their parameters are now set in stone and will not be altered when `Calculator.compute()`  is called. This can be useful for testing or small scale analysis but we may want a range of parameter specifications to be applied from a configuration specification.

#### General Objects
If we want parameterization to be applied in a configurable manner, we instead simply register the object itself:

    calc = Calculator(**calc_params)
    calc.register_custom_class(MyStatistic)
    calc.register_custom_class(MySummariser)
    calc.register_custom_class(MySummaryStatistic)

Now the classes will be made available for parameter injection from configuration specification instead.

### Grouping
If a higher quantity of custom statistics and/or summarisers are defined, it could be laborious to register them all individually. In this case, they can be registered en mass in a number of ways:

#### Iterable
Simply provide an iterable containing the objects in question. For specific instances:

    calc = Calculator(**calc_params)
    stat_1 = MyStatistic1(**stat_params_1)
    stat_2 = MyStatistic2(**stat_params_2)
    summariser = MySummariser(**summary_params)
    summary_stat = MySummaryStatistic(**summary_stat_params)
    custom_objects = [stat_1, stat_2, summariser, summary_stat]
    calc.register_custom_objects(custom_objects)

And for general classes open to configurable parameterisation:

    calc = Calculator(**calc_params)
    custom_classes = [MyStatistic1, MyStatistic2, MySummariser, MySummaryStatistic]
    calc.register_custom_classes(custom_classes)

This is useful when the number of objects is moderate. However, if a large number of objects are required - or one does not wish to load them all into memory - a better method is to register a module.

#### Module
An imported module can be registered in one command. However, note that this method does not allow for the definition of instantiated objects with pre-define parameters.

    import custom_stats
    calc = Calculator(**calc_params)
    calc.register_module(custom_stats)

All objects of the relevant type will be imported. Parameterisation must then come from an associated configuration file, instead. Finally, an option exists to perform this task without importing:

#### Python File

Similar to providing a module, one can simply provide the path to Python module file instead:

    calc = Calculator(**calc_params)
    path_to_module = "C:\...\custom_stats.py"
    calc.register_module_path(path_to_module)

The same method of extracting all objects of the relevant type will be applied as in **Module** example.
