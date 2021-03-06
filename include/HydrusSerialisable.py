import json
import lz4

SERIALISABLE_TYPE_BASE = 0
SERIALISABLE_TYPE_BASE_NAMED = 1
SERIALISABLE_TYPE_SHORTCUTS = 2
SERIALISABLE_TYPE_SUBSCRIPTION = 3
SERIALISABLE_TYPE_PERIODIC = 4
SERIALISABLE_TYPE_GALLERY_IDENTIFIER = 5
SERIALISABLE_TYPE_IMPORT_TAG_OPTIONS = 6
SERIALISABLE_TYPE_IMPORT_FILE_OPTIONS = 7
SERIALISABLE_TYPE_SEED_CACHE = 8
SERIALISABLE_TYPE_HDD_IMPORT = 9
SERIALISABLE_TYPE_SERVER_TO_CLIENT_CONTENT_UPDATE_PACKAGE = 10
SERIALISABLE_TYPE_SERVER_TO_CLIENT_SERVICE_UPDATE_PACKAGE = 11
SERIALISABLE_TYPE_MANAGEMENT_CONTROLLER = 12
SERIALISABLE_TYPE_GUI_SESSION = 13
SERIALISABLE_TYPE_PREDICATE = 14
SERIALISABLE_TYPE_FILE_SEARCH_CONTEXT = 15
SERIALISABLE_TYPE_EXPORT_FOLDER = 16
SERIALISABLE_TYPE_THREAD_WATCHER_IMPORT = 17
SERIALISABLE_TYPE_PAGE_OF_IMAGES_IMPORT = 18
SERIALISABLE_TYPE_IMPORT_FOLDER = 19
SERIALISABLE_TYPE_GALLERY_IMPORT = 20
SERIALISABLE_TYPE_DICTIONARY = 21
SERIALISABLE_TYPE_CLIENT_OPTIONS = 22
SERIALISABLE_TYPE_CONTENT = 23
SERIALISABLE_TYPE_SERVER_TO_CLIENT_PETITION = 24
SERIALISABLE_TYPE_ACCOUNT_IDENTIFIER = 25
SERIALISABLE_TYPE_LIST = 26

SERIALISABLE_TYPES_TO_OBJECT_TYPES = {}

def CreateFromNetworkString( network_string ):
    
    obj_string = lz4.loads( network_string )
    
    return CreateFromString( obj_string )
    
def CreateFromString( obj_string ):
    
    obj_tuple = json.loads( obj_string )
    
    return CreateFromSerialisableTuple( obj_tuple )
    
def CreateFromSerialisableTuple( obj_tuple ):
    
    if len( obj_tuple ) == 3:
        
        ( serialisable_type, version, serialisable_info ) = obj_tuple
        
        obj = SERIALISABLE_TYPES_TO_OBJECT_TYPES[ serialisable_type ]()
        
    else:
        
        ( serialisable_type, name, version, serialisable_info ) = obj_tuple
        
        obj = SERIALISABLE_TYPES_TO_OBJECT_TYPES[ serialisable_type ]( name )
        
    
    obj.InitialiseFromSerialisableInfo( version, serialisable_info )
    
    return obj
    
class SerialisableBase( object ):
    
    SERIALISABLE_TYPE = SERIALISABLE_TYPE_BASE
    SERIALISABLE_VERSION = 1
    
    def _GetSerialisableInfo( self ):
        
        raise NotImplementedError()
        
    
    def _InitialiseFromSerialisableInfo( self, serialisable_info ):
        
        raise NotImplementedError()
        
    
    def _UpdateSerialisableInfo( self, version, old_serialisable_info ):
        
        return old_serialisable_info
        
        
    def DumpToNetworkString( self ):
        
        obj_string = self.DumpToString()
        
        return lz4.dumps( obj_string )
        
    
    def DumpToString( self ):
        
        obj_tuple = self.GetSerialisableTuple()
        
        return json.dumps( obj_tuple )
        
    
    def GetSerialisableTuple( self ):
        
        return ( self.SERIALISABLE_TYPE, self.SERIALISABLE_VERSION, self._GetSerialisableInfo() )
        
    
    def InitialiseFromSerialisableInfo( self, version, serialisable_info ):
        
        while version < self.SERIALISABLE_VERSION:
            
            ( version, serialisable_info ) = self._UpdateSerialisableInfo( version, serialisable_info )
            
        
        self._InitialiseFromSerialisableInfo( serialisable_info )
        
    
class SerialisableBaseNamed( SerialisableBase ):
    
    SERIALISABLE_TYPE = SERIALISABLE_TYPE_BASE_NAMED
    
    def __init__( self, name ):
        
        SerialisableBase.__init__( self )
        
        self._name = name
        
    
    def GetSerialisableTuple( self ):
        
        return ( self.SERIALISABLE_TYPE, self._name, self.SERIALISABLE_VERSION, self._GetSerialisableInfo() )
        

    def GetName( self ): return self._name
    
    def SetName( self, name ): self._name = name
    
class SerialisableDictionary( SerialisableBase, dict ):
    
    SERIALISABLE_TYPE = SERIALISABLE_TYPE_DICTIONARY
    SERIALISABLE_VERSION = 1
    
    def __init__( self, *args, **kwargs ):
        
        dict.__init__( self, *args, **kwargs )
        SerialisableBase.__init__( self )
        
    
    def _GetSerialisableInfo( self ):
        
        simple_key_simple_value_pairs = []
        simple_key_serialisable_value_pairs = []
        serialisable_key_simple_value_pairs = []
        serialisable_key_serialisable_value_pairs = []
        
        for ( key, value ) in self.items():
            
            if isinstance( key, SerialisableBase ):
                
                serialisable_key = key.GetSerialisableTuple()
                
                if isinstance( value, SerialisableBase ):
                    
                    serialisable_value = value.GetSerialisableTuple()
                    
                    serialisable_key_serialisable_value_pairs.append( ( serialisable_key, serialisable_value ) )
                    
                else:
                    
                    serialisable_value = value
                    
                    serialisable_key_simple_value_pairs.append( ( serialisable_key, serialisable_value ) )
                    
                
            else:
                
                serialisable_key = key
                
                if isinstance( value, SerialisableBase ):
                    
                    serialisable_value = value.GetSerialisableTuple()
                    
                    simple_key_serialisable_value_pairs.append( ( serialisable_key, serialisable_value ) )
                    
                else:
                    
                    serialisable_value = value
                    
                    simple_key_simple_value_pairs.append( ( serialisable_key, serialisable_value ) )
                    
                
            
        
        return ( simple_key_simple_value_pairs, simple_key_serialisable_value_pairs, serialisable_key_simple_value_pairs, serialisable_key_serialisable_value_pairs )
        
    
    def _InitialiseFromSerialisableInfo( self, serialisable_info ):
        
        ( simple_key_simple_value_pairs, simple_key_serialisable_value_pairs, serialisable_key_simple_value_pairs, serialisable_key_serialisable_value_pairs ) = serialisable_info
        
        for ( key, value ) in simple_key_simple_value_pairs:
            
            self[ key ] = value
            
        
        for ( key, serialisable_value ) in simple_key_serialisable_value_pairs:
            
            value = CreateFromSerialisableTuple( serialisable_value )
            
            self[ key ] = value
            
        
        for ( serialisable_key, value ) in serialisable_key_simple_value_pairs:
            
            key = CreateFromSerialisableTuple( serialisable_key )
            
            self[ key ] = value
            
        
        for ( serialisable_key, serialisable_value ) in serialisable_key_serialisable_value_pairs:
            
            key = CreateFromSerialisableTuple( serialisable_key )
            
            value = CreateFromSerialisableTuple( serialisable_value )
            
            self[ key ] = value
            
        
    
SERIALISABLE_TYPES_TO_OBJECT_TYPES[ SERIALISABLE_TYPE_DICTIONARY ] = SerialisableDictionary

class SerialisableList( SerialisableBase, list ):
    
    SERIALISABLE_TYPE = SERIALISABLE_TYPE_LIST
    SERIALISABLE_VERSION = 1
    
    def __init__( self, *args, **kwargs ):
        
        list.__init__( self, *args, **kwargs )
        SerialisableBase.__init__( self )
        
    
    def _GetSerialisableInfo( self ):
        
        return [ obj.GetSerialisableTuple() for obj in self ]
        
    
    def _InitialiseFromSerialisableInfo( self, serialisable_info ):
        
        for obj_tuple in serialisable_info:
            
            self.append( CreateFromSerialisableTuple( obj_tuple ) )
            
        
    
SERIALISABLE_TYPES_TO_OBJECT_TYPES[ SERIALISABLE_TYPE_LIST ] = SerialisableList